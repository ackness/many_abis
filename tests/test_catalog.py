import json
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from eth_utils import keccak, to_checksum_address


ROOT = Path(__file__).resolve().parents[1]
ASSETS_ROOT = ROOT / "many_abis" / "assets"
CONTRACT_INDEX = ASSETS_ROOT / "contract-index.json"
TOKEN_INDEX = ASSETS_ROOT / "token-index.json"
VERIFICATION_INDEX = ASSETS_ROOT / "verification-snapshots.json"
VERIFICATION_SOURCE = ROOT / "registry" / "verification-snapshots.json"


class GeneratedCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contracts = json.loads(
            CONTRACT_INDEX.read_text(encoding="utf-8")
        )["contracts"]
        cls.tokens = json.loads(TOKEN_INDEX.read_text(encoding="utf-8"))["tokens"]
        cls.verifications = json.loads(
            VERIFICATION_INDEX.read_text(encoding="utf-8")
        )["snapshots"]
        cls.chains = json.loads(
            (ASSETS_ROOT / "utils" / "chains.json").read_text(encoding="utf-8")
        )

    def test_catalogs_cover_every_runtime_contract(self):
        expected_contracts = 0
        expected_tokens = 0
        expected_verifications = set()
        for chain_slug, chain in self.chains.items():
            expected_contracts += len(chain["dex"]) * 2
            expected_tokens += len(chain["stable_coins"])
            expected_tokens += len(chain.get("test_coins", {}))
            expected_tokens += 1
            addresses = {chain["weth"]["address"].lower()}
            for field in ("stable_coins", "test_coins"):
                addresses.update(
                    address.lower() for address in chain.get(field, {}).values()
                )
            for dex in chain["dex"].values():
                addresses.add(dex["factory_address"].lower())
                addresses.add(dex["router_address"].lower())
            expected_verifications.update(
                "{}:{}".format(chain_slug, address) for address in addresses
            )
        expected_contracts += expected_tokens

        self.assertEqual(len(self.contracts), expected_contracts)
        self.assertEqual(len(self.contracts), 99)
        self.assertEqual(len(self.tokens), expected_tokens)
        self.assertEqual(len(self.tokens), 53)
        self.assertEqual(
            {record["verification_id"] for record in self.contracts.values()},
            expected_verifications,
        )
        self.assertEqual(set(self.verifications), expected_verifications)
        self.assertEqual(len(self.verifications), 99)

    def test_snapshot_source_exactly_generates_runtime_evidence(self):
        source = json.loads(VERIFICATION_SOURCE.read_text(encoding="utf-8"))
        self.assertEqual(source["snapshots"], self.verifications)
        for verification_id, snapshot in self.verifications.items():
            chain = self.chains[snapshot["chain"]]
            with self.subTest(verification=verification_id):
                self.assertEqual(snapshot["chain_id"], chain["chain_id"])
                self.assertIn(snapshot["rpc_url"], chain["rpc"])
                self.assertGreater(snapshot["block_number"], 0)
                self.assertGreater(snapshot["code_size"], 0)
                self.assertRegex(snapshot["block_hash"], r"^0x[0-9a-f]{64}$")
                self.assertRegex(
                    snapshot["runtime_code_keccak256"], r"^0x[0-9a-f]{64}$"
                )
                implementation = snapshot["eip1967"]["implementation"]
                implementation_hash = snapshot["eip1967"][
                    "implementation_code_keccak256"
                ]
                self.assertEqual(
                    implementation is None,
                    implementation_hash is None,
                )

    def test_token_catalog_preserves_configured_and_observed_identity(self):
        for token_id, token in self.tokens.items():
            snapshot = self.verifications[token["verification_id"]]
            with self.subTest(token=token_id):
                self.assertEqual(
                    token["observed_symbol"],
                    snapshot["token_metadata"]["symbol"],
                )
                self.assertEqual(
                    token["decimals"],
                    snapshot["token_metadata"]["decimals"],
                )
                if (
                    token["role"] == "stablecoin"
                    and token["origin"] != "unknown"
                ):
                    self.assertTrue(token["evidence_url"])
        self.assertEqual(self.tokens["base:USDC"]["origin"], "issuer_native")
        self.assertEqual(self.tokens["base:USDC"]["decimals"], 6)
        self.assertEqual(self.tokens["arbitrum:USDT0"]["origin"], "bridged")
        self.assertEqual(
            self.tokens["arbitrum:USDT0"]["observed_symbol"], "USD₮0"
        )
        self.assertEqual(self.tokens["avalanche:USDT"]["origin"], "unknown")

    def test_address_validation_rejects_zero_and_bad_checksum(self):
        from scripts.generate_registry import RegistryError, _validate_address

        with self.assertRaises(RegistryError):
            _validate_address("0x" + "0" * 40, "test")

        valid = to_checksum_address("0x833589fcd6edb6e08f4c7c32d4f71b54bda02913")
        position = next(
            index
            for index, character in enumerate(valid[2:], start=2)
            if character.isalpha()
        )
        replacement = valid[position].swapcase()
        invalid = valid[:position] + replacement + valid[position + 1 :]
        with self.assertRaises(RegistryError):
            _validate_address(invalid, "test")

    def test_refresh_helpers_use_exact_slots_and_decode_token_symbols(self):
        from scripts.refresh_verifications import (
            ADMIN_SLOT,
            BEACON_SLOT,
            IMPLEMENTATION_SLOT,
            VerificationError,
            _chain_targets,
            _decode_symbol,
            _decode_uint8,
            _storage_address,
        )

        for label, slot in (
            ("eip1967.proxy.implementation", IMPLEMENTATION_SLOT),
            ("eip1967.proxy.admin", ADMIN_SLOT),
            ("eip1967.proxy.beacon", BEACON_SLOT),
        ):
            expected = int.from_bytes(keccak(text=label), "big") - 1
            self.assertEqual(slot, "0x" + expected.to_bytes(32, "big").hex())

        symbol = "USD₮0".encode("utf-8")
        dynamic = (
            (32).to_bytes(32, "big")
            + len(symbol).to_bytes(32, "big")
            + symbol.ljust(32, b"\x00")
        )
        self.assertEqual(_decode_symbol("0x" + dynamic.hex()), "USD₮0")
        self.assertEqual(
            _decode_symbol("0x" + b"USDC".ljust(32, b"\x00").hex()),
            "USDC",
        )
        self.assertIsNone(_storage_address("0x" + "0" * 64))

        shared = to_checksum_address("0x" + "1" * 40)
        other = to_checksum_address("0x" + "2" * 40)
        targets = _chain_targets(
            {
                "weth": {"address": shared},
                "stable_coins": {},
                "test_coins": {},
                "dex": {
                    "shared": {
                        "factory_address": shared.lower(),
                        "router_address": other,
                    }
                },
            }
        )
        self.assertEqual(len(targets), 2)
        self.assertEqual(targets[shared.lower()], (shared, True))

        malformed_values = (
            lambda: _storage_address("0x" + "0" * 62),
            lambda: _storage_address("0x01" + "0" * 62),
            lambda: _decode_uint8("0x01", "decimals()"),
            lambda: _decode_uint8("0x" + "0" * 60 + "0100", "decimals()"),
            lambda: _decode_symbol(
                "0x"
                + (32).to_bytes(32, "big").hex()
                + (4).to_bytes(32, "big").hex()
                + b"US".hex()
            ),
        )
        for decode in malformed_values:
            with self.assertRaises(VerificationError):
                decode()

    def test_refresh_rejects_a_block_hash_change(self):
        from scripts.refresh_verifications import VerificationError, _confirm_block

        changed_block = {"number": "0x2a", "hash": "0x" + "2" * 64}
        with patch(
            "scripts.refresh_verifications._rpc_call",
            return_value=changed_block,
        ):
            with self.assertRaises(VerificationError):
                _confirm_block(
                    Mock(),
                    "https://rpc.example",
                    "0x2a",
                    42,
                    "0x" + "1" * 64,
                    1.0,
                )


class RuntimeCatalogTests(unittest.TestCase):
    def setUp(self):
        import many_abis as ma

        self.ma = ma

    def test_abi_metadata_queries_are_defensive(self):
        info = self.ma.get_abi_info("erc5267")
        self.assertEqual(info["interface_name"], "IERC5267")
        info["interface_name"] = "changed"
        self.assertEqual(
            self.ma.get_abi_info("ERC5267")["interface_name"], "IERC5267"
        )
        self.assertIn("ERC5267", self.ma.find_abis(contract_role="signature"))
        self.assertEqual(
            self.ma.find_abis(interface_name="IERC5267"),
            ["ERC5267"],
        )
        with self.assertRaises(KeyError):
            self.ma.get_abi_info("not-real")

    def test_contract_queries_filter_and_return_copies(self):
        self.assertEqual(len(self.ma.all_contract_ids()), 99)
        contract = self.ma.get_contract("BASE:DEX:UNISWAP-V3:ROUTER")
        self.assertEqual(contract["abi"], "UNISWAP_V3_ROUTER_02")
        self.assertIn("source_reviewed_at", contract)
        self.assertNotIn("verified_at", contract)
        contract["abi"] = "changed"
        self.assertEqual(
            self.ma.get_contract("base:dex:uniswap-v3:router")["abi"],
            "UNISWAP_V3_ROUTER_02",
        )
        self.assertEqual(
            len(self.ma.list_contracts(chain="base", protocol="uniswap_v3")),
            2,
        )
        with self.assertRaises(KeyError):
            self.ma.get_contract("base:not-real")

    def test_token_and_verification_queries(self):
        self.assertEqual(len(self.ma.all_token_ids()), 53)
        token = self.ma.get_token("BASE", "usdc")
        self.assertEqual(token["decimals"], 6)
        self.assertEqual(token["origin"], "issuer_native")
        self.assertTrue(self.ma.list_tokens(origin="bridged"))

        by_slug = self.ma.get_verification("base", token["address"])
        by_chain_id = self.ma.get_verification(8453, token["address"])
        self.assertEqual(by_slug, by_chain_id)
        by_slug["code_size"] = 0
        self.assertGreater(
            self.ma.get_verification("base", token["address"])["code_size"], 0
        )
        with self.assertRaises(ValueError):
            self.ma.get_verification("base", "not-an-address")
        with self.assertRaises(KeyError):
            self.ma.get_verification("base", "0x" + "1" * 40)


if __name__ == "__main__":
    unittest.main()
