"""Opt-in, read-only checks against registered RPCs; never sign transactions.

Run with MANY_ABIS_LIVE_TESTS=1 uv run --with web3 python -m unittest
discover -s tests -p test_singleton_live.py -v. An optional MANY_ABIS_LIVE_CHAIN
limits deployment checks to one chain. Pool fixtures are always checked only
on their own chain.
"""

import json
import os
import unittest
from copy import deepcopy
from pathlib import Path

import many_abis as ma


ROOT = Path(__file__).resolve().parents[1]
ZERO = "0x" + "0" * 40


@unittest.skipUnless(os.environ.get("MANY_ABIS_LIVE_TESTS") == "1", "opt-in live RPC checks")
class SingletonLiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from web3 import Web3

        cls.Web3 = Web3
        cls.clients = {}
        cls.observations = []
        cls.chain_filter = os.environ.get("MANY_ABIS_LIVE_CHAIN")
        cls.records = [
            record for record in ma.list_contracts()
            if "deployment_version" in record
            and (cls.chain_filter is None or record["chain"] == cls.chain_filter)
        ]
        if not cls.records:
            raise AssertionError("no explicit deployments selected")

    @classmethod
    def tearDownClass(cls):
        report = os.environ.get("MANY_ABIS_READ_REPORT")
        if report:
            Path(report).write_text(
                json.dumps(cls.observations, indent=2) + "\n", encoding="utf-8"
            )

    def client(self, slug):
        if slug not in self.clients:
            chain = ma.get_chain(name=slug)
            failures = []
            for url in chain["rpc"]:
                w3 = self.Web3(self.Web3.HTTPProvider(url, request_kwargs={"timeout": 20}))
                try:
                    self.assertEqual(w3.eth.chain_id, chain["chain_id"])
                    number = w3.eth.block_number
                    # Direct RPC avoids chain-specific extraData middleware.
                    block = w3.provider.make_request("eth_getBlockByNumber", [hex(number), False])["result"]
                    self.clients[slug] = (w3, number, block["hash"])
                    break
                except Exception as exc:
                    failures.append(type(exc).__name__)
            else:
                self.fail("{} RPCs unavailable: {}".format(slug, failures))
        return self.clients[slug]

    def contract(self, record):
        w3, block, block_hash = self.client(record["chain"])
        contract = w3.eth.contract(
            address=self.Web3.to_checksum_address(record["address"]),
            abi=deepcopy(ma.get_abi(record["abi"])),
        )
        return w3, contract, block, block_hash

    def observe(self, record, function, arguments=()):
        w3, contract, block, block_hash = self.contract(record)
        result = getattr(contract.functions, function)(*arguments).call(block_identifier=block)
        from examples.singleton_pools import _jsonable

        self.observations.append({
            "contract_id": record["contract_id"], "block_number": block,
            "block_hash": block_hash, "function": function,
            "arguments": _jsonable(arguments), "result": _jsonable(result),
        })
        return result

    def test_deployed_code_and_read_getters(self):
        for record in self.records:
            with self.subTest(contract=record["contract_id"]):
                w3, contract, block, _ = self.contract(record)
                code = w3.eth.get_code(contract.address, block_identifier=block)
                self.assertTrue(code)
                snapshot = ma.get_verification(record["chain"], record["address"])
                self.assertEqual(
                    "0x" + self.Web3.keccak(code).hex(), snapshot["runtime_code_keccak256"]
                )
                functions = {
                    item["name"]: item for item in contract.abi
                    if item["type"] == "function"
                }
                for name in (
                    "poolManager", "clPoolManager", "binPoolManager", "vault",
                    "permit2", "V4_POOL_MANAGER", "V4_POSITION_MANAGER",
                    "INFI_CL_POSITION_MANAGER", "INFI_BIN_POSITION_MANAGER",
                    "nextTokenId", "name", "symbol", "MIN_BIN_STEP", "maxBinStep", "getLocker",
                ):
                    item = functions.get(name)
                    if item is None or item["inputs"]:
                        continue
                    result = self.observe(record, name)
                    expected = self.expected_dependency(record, name)
                    if expected is not None:
                        self.assertEqual(result.lower(), expected.lower())
                    elif name == "nextTokenId":
                        self.assertGreater(result, 0)
                if record["role"] == "permit2":
                    token = self.Web3.to_checksum_address(
                        ma.get_chain(name=record["chain"])["weth"]["address"]
                    )
                    allowance = self.observe(record, "allowance", (ZERO, token, ZERO))
                    self.assertEqual(tuple(allowance), (0, 0, 0))
                    self.assertEqual(self.observe(record, "nonceBitmap", (ZERO, 0)), 0)
                if record["role"] == "pool_manager" and "protocolFeesAccrued" in functions:
                    self.assertGreaterEqual(self.observe(record, "protocolFeesAccrued", (ZERO,)), 0)
                if record["role"] == "vault":
                    for kind in ("cl", "bin"):
                        manager = ma.get_contract(f"bsc:dex:pancake-infinity-{kind}:pool_manager")
                        self.assertTrue(self.observe(record, "isAppRegistered", (
                            self.Web3.to_checksum_address(manager["address"]),
                        )))
        for slug, (w3, block, expected_hash) in self.clients.items():
            with self.subTest(chain=slug, check="block consistency"):
                observed = w3.provider.make_request("eth_getBlockByNumber", [hex(block), False])["result"]
                self.assertEqual(observed["hash"], expected_hash)

    def expected_dependency(self, record, getter):
        slug = record["chain"]
        if record["protocol"] == "uniswap":
            targets = {
                "poolManager": "uniswap-v4:pool_manager",
                "V4_POOL_MANAGER": "uniswap-v4:pool_manager",
                "V4_POSITION_MANAGER": "uniswap-v4:position_manager",
                "permit2": "uniswap-permit2:permit2",
            }
        else:
            if getter == "poolManager":
                target_id = record["contract_id"].rsplit(":", 1)[0] + ":pool_manager"
                return ma.get_contract(target_id)["address"]
            targets = {
                "clPoolManager": "pancake-infinity-cl:pool_manager",
                "binPoolManager": "pancake-infinity-bin:pool_manager",
                "vault": "pancake-infinity:vault",
                "permit2": "pancake-infinity:permit2",
                "INFI_CL_POSITION_MANAGER": "pancake-infinity-cl:position_manager",
                "INFI_BIN_POSITION_MANAGER": "pancake-infinity-bin:position_manager",
            }
        target = targets.get(getter)
        return ma.get_contract(f"{slug}:dex:{target}")["address"] if target else None

    def test_initialized_pool_state_and_quote(self):
        from hexbytes import HexBytes
        from examples.singleton_pools import _pool_key, pool_id_for_key

        fixtures = json.loads((ROOT / "tests/fixtures/singleton-pools.json").read_text(encoding="utf-8"))
        selected = [f for f in fixtures if self.chain_filter is None or f["chain"] == self.chain_filter]
        if not selected:
            self.skipTest("no initialized pool fixture for this chain")
        for fixture in selected:
            slug, protocol = fixture["chain"], fixture["protocol"]
            with self.subTest(chain=slug, protocol=protocol):
                w3, block, block_hash = self.client(slug)
                key = _pool_key(fixture["pool_key"], protocol, self.Web3, HexBytes)
                pool_id = pool_id_for_key(w3, protocol, key)
                self.assertEqual("0x" + pool_id.hex(), fixture["pool_id"])
                role = "state_view" if protocol == "uniswap-v4" else "pool_manager"
                reader = ma.get_contract(f"{slug}:dex:{protocol}:{role}")
                slot0 = self.observe(reader, "getSlot0", (pool_id,))
                self.assertGreater(slot0[0], 0)
                if protocol == "pancake-infinity-bin":
                    reserves = self.observe(reader, "getBin", (pool_id, slot0[0]))
                    self.assertGreater(reserves[0] + reserves[1], 0)
                else:
                    self.assertGreater(self.observe(reader, "getLiquidity", (pool_id,)), 0)
                if protocol != "uniswap-v4":
                    observed_key = self.observe(reader, "poolIdToPoolKey", (pool_id,))
                    self.assertEqual(pool_id_for_key(w3, protocol, observed_key), pool_id)
                quoter = ma.get_contract(f"{slug}:dex:{protocol}:quoter")
                amount_out, gas = self.observe(quoter, "quoteExactInputSingle", (
                    (key, fixture["zero_for_one"], fixture["amount_in"], b""),
                ))
                self.assertGreater(amount_out, 0)
                self.assertGreater(gas, 0)
                confirmed = w3.provider.make_request("eth_getBlockByNumber", [hex(block), False])["result"]
                self.assertEqual(confirmed["hash"], block_hash)


if __name__ == "__main__":
    unittest.main()
