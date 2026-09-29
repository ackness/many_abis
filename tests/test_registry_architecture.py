import ast
import hashlib
import json
import subprocess
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "many_abis"
ASSETS_ROOT = PACKAGE_ROOT / "assets"
CHAIN_OUTPUT = ASSETS_ROOT / "utils" / "chains.json"
ABI_INDEX = ASSETS_ROOT / "abi-index.json"


class GeneratedRegistryTests(unittest.TestCase):
    def test_generated_outputs_are_current(self):
        result = subprocess.run(
            [sys.executable, "scripts/generate_registry.py", "--check"],
            cwd=str(ROOT),
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_per_chain_sources_exactly_generate_runtime_data(self):
        order = json.loads(
            (ROOT / "registry" / "chain-order.json").read_text(encoding="utf-8")
        )["chains"]
        runtime = json.loads(CHAIN_OUTPUT.read_text(encoding="utf-8"))
        sources = {}
        for slug in order:
            source = json.loads(
                (ROOT / "registry" / "chains" / (slug + ".json")).read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(source["slug"], slug)
            self.assertTrue(source["provenance"]["chain"].startswith("https://"))
            sources[slug] = source["data"]

        self.assertEqual(list(runtime), order)
        self.assertEqual(runtime, sources)

    def test_abi_manifest_covers_every_asset_and_hashes_content(self):
        manifest = json.loads(ABI_INDEX.read_text(encoding="utf-8"))["abis"]
        abi_paths = sorted(ASSETS_ROOT.rglob("*.abi"))

        self.assertEqual(len(manifest), len(abi_paths))
        self.assertGreater(len(manifest), 37)
        self.assertEqual(
            {entry["resource"] for entry in manifest.values()},
            {
                path.relative_to(PACKAGE_ROOT).as_posix()
                for path in abi_paths
            },
        )
        for name, entry in manifest.items():
            path = PACKAGE_ROOT / entry["resource"]
            abi = json.loads(path.read_text(encoding="utf-8"))
            canonical = json.dumps(
                abi, ensure_ascii=False, separators=(",", ":"), sort_keys=True
            ).encode("utf-8")
            with self.subTest(abi=name):
                self.assertEqual(
                    hashlib.sha256(canonical).hexdigest(),
                    entry["canonical_sha256"],
                )
                self.assertEqual(len(abi), entry["item_count"])

    def test_audited_and_legacy_inventories_are_explicit_and_disjoint(self):
        manifest = json.loads(ABI_INDEX.read_text(encoding="utf-8"))["abis"]
        audited = json.loads(
            (ROOT / "registry" / "abi-metadata.json").read_text(encoding="utf-8")
        )["abis"]
        legacy = json.loads(
            (ROOT / "registry" / "legacy-abi-allowlist.json").read_text(
                encoding="utf-8"
            )
        )["abis"]

        self.assertEqual(set(audited), set(manifest))
        self.assertTrue(set(audited).isdisjoint(legacy))
        self.assertGreater(len(audited), 37)
        self.assertEqual(len(legacy), 40)
        for name, details in audited.items():
            with self.subTest(abi=name):
                self.assertEqual(
                    details["canonical_sha256"],
                    manifest[name]["canonical_sha256"],
                )

        quarantine_root = ROOT / "registry" / "legacy-abis"
        quarantined = {}
        for path in quarantine_root.rglob("*.abi"):
            parts = path.relative_to(quarantine_root).with_suffix("").parts[1:]
            name = "_".join(parts).upper()
            abi = json.loads(path.read_text(encoding="utf-8"))
            canonical = json.dumps(
                abi, ensure_ascii=False, separators=(",", ":"), sort_keys=True
            ).encode("utf-8")
            quarantined[name] = hashlib.sha256(canonical).hexdigest()

        self.assertEqual(set(quarantined), set(legacy))
        self.assertTrue(set(quarantined).isdisjoint(manifest))
        for name, canonical_sha256 in quarantined.items():
            with self.subTest(quarantined_abi=name):
                self.assertEqual(
                    canonical_sha256,
                    legacy[name]["canonical_sha256"],
                )

        from many_abis.meta import ABIMetaData

        self.assertEqual(set(ABIMetaData.__annotations__), set(audited))

    def test_runtime_abi_references_are_audited(self):
        chains = json.loads(CHAIN_OUTPUT.read_text(encoding="utf-8"))
        manifest = json.loads(ABI_INDEX.read_text(encoding="utf-8"))["abis"]
        for chain_slug, chain in chains.items():
            for dex_slug, dex in chain["dex"].items():
                for role in ("factory", "router"):
                    name = dex.get(role + "_abi")
                    if name is None:
                        continue
                    with self.subTest(chain=chain_slug, dex=dex_slug, role=role):
                        self.assertEqual(manifest[name]["contract_role"], role)
                        self.assertEqual(manifest[name]["provenance"]["status"], "verified")
                        self.assertEqual(
                            manifest[name]["license"]["redistribution"], "allowed"
                        )

    def test_schema_rejects_incomplete_dex(self):
        from jsonschema import Draft202012Validator, FormatChecker

        schema = json.loads(
            (ROOT / "registry" / "schemas" / "chain-source.schema.json").read_text(
                encoding="utf-8"
            )
        )
        source = json.loads(
            (ROOT / "registry" / "chains" / "base.json").read_text(
                encoding="utf-8"
            )
        )
        del source["data"]["dex"]["uniswap_v3"]["router_address"]
        errors = list(
            Draft202012Validator(
                schema, format_checker=FormatChecker()
            ).iter_errors(source)
        )

        self.assertTrue(errors)

    def test_rpc_urls_reject_credentials_query_and_fragment(self):
        from jsonschema import Draft202012Validator, FormatChecker

        from scripts.generate_registry import RegistryError, _validate_chain

        schema = json.loads(
            (ROOT / "registry" / "schemas" / "chain-source.schema.json").read_text(
                encoding="utf-8"
            )
        )
        source = json.loads(
            (ROOT / "registry" / "chains" / "base.json").read_text(
                encoding="utf-8"
            )
        )
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        invalid_urls = (
            "https://user:password@rpc.example/path",
            "https://rpc.example/path?api_key=secret",
            "https://rpc.example/path#fragment",
        )
        for rpc_url in invalid_urls:
            candidate = deepcopy(source)
            candidate["data"]["rpc"] = [rpc_url]
            with self.subTest(rpc_url=rpc_url):
                self.assertTrue(list(validator.iter_errors(candidate)))
                with self.assertRaises(RegistryError):
                    _validate_chain("base", candidate)

        candidate = deepcopy(source)
        candidate["data"]["rpc"] = ["https://rpc.example/path/to/endpoint"]
        self.assertFalse(list(validator.iter_errors(candidate)))
        self.assertEqual(
            _validate_chain("base", candidate)["rpc"],
            candidate["data"]["rpc"],
        )

    def test_historically_mislabeled_abis_are_corrected(self):
        checks = {
            "PANCAKE_V3_POOL_V3": ("swap", "createPool"),
            "AAVE_V2_LENDING_POOL_ADDRESSES_PROVIDER": (
                "getLendingPool",
                "CORE_REVISION",
            ),
            "UNISWAP_V1_EXCHANGE": ("tokenToTokenSwapInput", "getSymbol"),
        }
        manifest = json.loads(ABI_INDEX.read_text(encoding="utf-8"))["abis"]
        self.assertEqual(
            manifest["AAVE_V2_LENDING_POOL_ADDRESSES_PROVIDER"]["contract_role"],
            "other",
        )
        self.assertEqual(
            manifest["AAVE_V2_LENDING_POOL_ADDRESSES_PROVIDER"]["license"][
                "spdx_expression"
            ],
            "AGPL-3.0-or-later",
        )
        self.assertEqual(manifest["UNISWAP_V1_EXCHANGE"]["contract_role"], "pool")
        for name, (required, forbidden) in checks.items():
            abi = json.loads(
                (PACKAGE_ROOT / manifest[name]["resource"]).read_text(encoding="utf-8")
            )
            function_names = {
                item.get("name") for item in abi if item.get("type") == "function"
            }
            with self.subTest(abi=name):
                self.assertIn(required, function_names)
                self.assertNotIn(forbidden, function_names)

    def test_common_contract_abis_match_fixed_official_artifacts(self):
        expected = {
            "CHAINLINK_AGGREGATOR_V3": (
                "4033192d711ea3401146cf48e206b62afd431607247832fd4577a9887f89dbeb",
                "oracle",
                5,
            ),
            "ERC1271": (
                "5721ab6bdea982cbd7690bcc59d90ba0b53da853a52c50fbeeb0cb88de1dcf4b",
                "signature",
                1,
            ),
            "ERC165": (
                "fc839607f64e5467d99b3595b1238161897b3d186fa7ddc7d190df4b4e73ca46",
                "utility",
                1,
            ),
            "ERC20_PERMIT": (
                "0870cfbd0a83906160018e9917de6b4a4999d5d7f157134df2bbd468e18e3df3",
                "token",
                3,
            ),
            "ERC2981": (
                "aacd60a298b69f44e9d96171c56834a694c547138a5eb0c6a45ac5c905db20ca",
                "token",
                2,
            ),
            "ERC4626": (
                "88aba979731928030849ebbb33cfecbf95e4d6745bd208fd29957ddffa18278e",
                "vault",
                29,
            ),
            "ERC5267": (
                "f1e87151c8635b01ae77e263e813ceeb486d9df6c35300055cb85c248421f55f",
                "signature",
                2,
            ),
            "ERC6093_ERC1155_ERRORS": (
                "4788991d085e0b9990603501d1cab5fcb830c3429fad3d59a421afc27d2ab708",
                "utility",
                7,
            ),
            "ERC6093_ERC20_ERRORS": (
                "851ca5f5bf60a11262c78d710c46d935f0d7dde2b760ba7d7f199d273d2bcf71",
                "utility",
                6,
            ),
            "ERC6093_ERC721_ERRORS": (
                "22cb31c1805339cc470a1ef3b5cb08b468e465bd624e68529ea9b72fbb87621f",
                "utility",
                8,
            ),
            "ERC6909": (
                "30b53c3e4dbd8581092b18d2fc237e39dc152007f9d73de64a466c119b7b6cab",
                "token",
                11,
            ),
            "ERC6909_METADATA": (
                "494be78ce5cbcc90d0fcb6ba3060009ef83058f0fe079f2df87e4570798baad9",
                "token",
                14,
            ),
            "MULTICALL3": (
                "2407bc7c0820a63c0b5221e3344b86d28de2f2166b78a098361cab65d5506c4e",
                "utility",
                16,
            ),
            "OPENZEPPELIN_ACCESS_CONTROL_V5": (
                "bc72d531de7a497a2bf073bc17ab61882bb79de92e1a1ebdd81134246a92eb8d",
                "access",
                10,
            ),
            "OPENZEPPELIN_IERC1967": (
                "8fe688091f63e8483a5ffac5ed387ab69faa4cc6e58ca237031d5a94e18bf8af",
                "proxy",
                3,
            ),
            "UNISWAP_PERMIT2": (
                "28c807df09f0d09db5a55b95280d544ca01952232e393f76f00ccb4b37cc3ef0",
                "token",
                31,
            ),
            "UNISWAP_V3_POOL_EVENTS": (
                "666acad093a50294d65df87845456ae2a8882e6037160320dd2cfe55735acb1a",
                "pool",
                9,
            ),
            "UNISWAP_V3_POOL_STATE": (
                "b74b941dd9da63369720494e5596d7370d7bb25902f62581f790bdd2591e03ed",
                "pool",
                9,
            ),
        }
        manifest = json.loads(ABI_INDEX.read_text(encoding="utf-8"))["abis"]

        for name, (canonical_hash, role, item_count) in expected.items():
            entry = manifest[name]
            with self.subTest(abi=name):
                self.assertEqual(entry["canonical_sha256"], canonical_hash)
                self.assertEqual(entry["contract_role"], role)
                self.assertEqual(entry["item_count"], item_count)
                self.assertEqual(entry["provenance"]["status"], "verified")
                self.assertTrue(entry["provenance"]["artifact_path"])
                self.assertEqual(entry["license"]["redistribution"], "allowed")

        proxy_events = json.loads(
            (
                PACKAGE_ROOT
                / manifest["OPENZEPPELIN_IERC1967"]["resource"]
            ).read_text(encoding="utf-8")
        )
        self.assertTrue(proxy_events)
        self.assertEqual({item["type"] for item in proxy_events}, {"event"})

        permit = json.loads(
            (PACKAGE_ROOT / manifest["ERC20_PERMIT"]["resource"]).read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            {item["name"] for item in permit if item["type"] == "function"},
            {"DOMAIN_SEPARATOR", "nonces", "permit"},
        )

    def test_python_sources_parse_as_python_3_13(self):
        paths = (
            list(PACKAGE_ROOT.glob("*.py"))
            + list(PACKAGE_ROOT.glob("*.pyi"))
            + list((ROOT / "scripts").glob("*.py"))
        )
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT)):
                ast.parse(
                    path.read_text(encoding="utf-8"),
                    filename=str(path),
                    feature_version=(3, 13),
                )


class RuntimeCompatibilityTests(unittest.TestCase):
    def setUp(self):
        import many_abis as ma

        self.ma = ma
        ma.clear_abi_cache()

    def test_import_and_listing_do_not_load_abi_assets(self):
        self.assertEqual(self.ma.loaded_abis(), [])

    def test_clean_import_neither_parses_abi_arrays_nor_accesses_network(self):
        code = r'''
import json
import eth_utils
import requests

original_loads = json.loads

def guarded_loads(*args, **kwargs):
    value = original_loads(*args, **kwargs)
    if isinstance(value, list):
        raise AssertionError("ABI array parsed during import")
    return value

def fail_network(*args, **kwargs):
    raise AssertionError("network accessed during import")

json.loads = guarded_loads
requests.Session.get = fail_network
import many_abis as ma
import many_abis.catalog as catalog
assert ma.loaded_abis() == []
assert len(ma.ALL_ABIS_NAME) > 37
assert catalog._CONTRACTS is None
assert catalog._TOKENS is None
assert catalog._VERIFICATIONS is None
'''
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=str(ROOT),
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertGreater(len(self.ma.ALL_ABIS_NAME), 37)
        self.assertEqual(len(self.ma.supported_abis()), len(self.ma.ALL_ABIS_NAME))
        self.assertEqual(self.ma.loaded_abis(), [])

    def test_verified_abi_access_loads_once(self):
        from addict import Dict

        first = self.ma.ABIS.ERC165
        self.assertIs(first, self.ma.ABIS["ERC165"])
        self.assertIs(first, self.ma.get_abi("erc165"))
        self.assertEqual(self.ma.loaded_abis(), ["ERC165"])
        self.assertIsInstance(first[0], Dict)
        self.assertEqual(first[0].type, first[0]["type"])

    def test_concurrent_first_access_returns_one_cached_object(self):
        with ThreadPoolExecutor(max_workers=8) as executor:
            values = list(executor.map(lambda _: self.ma.get_abi("ERC5267"), range(32)))

        self.assertTrue(all(value is values[0] for value in values))
        self.assertEqual(self.ma.loaded_abis(), ["ERC5267"])

    def test_load_abi_excludes_quarantined_legacy_content(self):
        with self.assertRaises(FileNotFoundError):
            self.ma.load_abi("erc/ERC20")

        first = self.ma.load_abi("contracts/erc165")
        second = self.ma.load_abi("contracts/erc165.abi")

        self.assertEqual(first, second)
        self.assertIsNot(first, second)
        self.assertIsInstance(first, list)
        self.assertIsInstance(first[0], dict)
        self.assertEqual(self.ma.loaded_abis(), [])

    def test_all_abis_returns_fresh_eager_addict_data(self):
        names, first = self.ma.all_abis()
        _, second = self.ma.all_abis()

        self.assertEqual(names, self.ma.ALL_ABIS_NAME)
        self.assertEqual(len(first), len(self.ma.ALL_ABIS_NAME))
        self.assertIsNot(first, second)
        self.assertIsNot(first.ERC165, second.ERC165)
        self.assertEqual(self.ma.loaded_abis(), [])

    def test_registry_copy_and_to_dict_keep_compatibility_shapes(self):
        from addict import Dict

        cached = self.ma.ABIS.ERC165
        shallow = self.ma.ABIS.copy()
        plain = self.ma.ABIS.to_dict()

        self.assertIsInstance(shallow, Dict)
        self.assertIs(shallow.ERC165, cached)
        self.assertIsInstance(plain, dict)
        self.assertNotIsInstance(plain["ERC165"][0], Dict)

    def test_registry_is_read_only_and_path_traversal_is_rejected(self):
        with self.assertRaises(TypeError):
            self.ma.ABIS["ERC165"] = []
        with self.assertRaises(AttributeError):
            self.ma.ABIS.ERC165 = []
        self.assertIn("ERC165", self.ma.ABIS)
        self.assertEqual(self.ma.loaded_abis(), [])
        with self.assertRaises(KeyError):
            self.ma.ABIS["NOT_REAL"]
        with self.assertRaises(AttributeError):
            self.ma.ABIS.NOT_REAL
        for unsafe in ("../setup", "/tmp/value", "erc\\ERC20"):
            with self.subTest(path=unsafe), self.assertRaises(ValueError):
                self.ma.load_abi(unsafe)

    def test_chain_api_compatibility_and_defensive_list_copy(self):
        chains = self.ma.all_chains()
        chains.clear()

        self.assertEqual(len(self.ma.all_chains()), 15)
        self.assertEqual(self.ma.chain(name="base").chain_id, 8453)
        self.assertEqual(self.ma.chain(chain_id=196).weth.symbol, "WOKB")
        with self.assertRaises(ValueError):
            self.ma.get_chain_by_name("not-a-chain")
        with self.assertRaises(ValueError):
            self.ma.get_chain()


if __name__ == "__main__":
    unittest.main()
