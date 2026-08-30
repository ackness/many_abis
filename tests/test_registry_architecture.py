import ast
import hashlib
import json
import subprocess
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
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
        self.assertEqual(len(manifest), 59)
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

        self.assertEqual(set(audited) | set(legacy), set(manifest))
        self.assertTrue(set(audited).isdisjoint(legacy))
        self.assertEqual(len(audited), 19)
        self.assertEqual(len(legacy), 40)
        for name, details in legacy.items():
            with self.subTest(abi=name):
                self.assertEqual(
                    details["canonical_sha256"],
                    manifest[name]["canonical_sha256"],
                )

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

    def test_python_sources_parse_as_python_3_8(self):
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
                    feature_version=(3, 8),
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
assert ma.loaded_abis() == []
assert len(ma.ALL_ABIS_NAME) == 59
'''
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=str(ROOT),
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(len(self.ma.ALL_ABIS_NAME), 59)
        self.assertEqual(len(self.ma.supported_abis()), 59)
        self.assertEqual(self.ma.loaded_abis(), [])

    def test_legacy_and_new_abi_access_load_once(self):
        from addict import Dict

        first = self.ma.ABIS.ERC20
        self.assertIs(first, self.ma.ABIS["ERC20"])
        self.assertIs(first, self.ma.get_abi("erc20"))
        self.assertEqual(self.ma.loaded_abis(), ["ERC20"])
        self.assertIsInstance(first[0], Dict)
        self.assertEqual(first[0].type, first[0]["type"])

    def test_concurrent_first_access_returns_one_cached_object(self):
        with ThreadPoolExecutor(max_workers=8) as executor:
            values = list(executor.map(lambda _: self.ma.get_abi("ERC721"), range(32)))

        self.assertTrue(all(value is values[0] for value in values))
        self.assertEqual(self.ma.loaded_abis(), ["ERC721"])

    def test_legacy_load_abi_is_eager_and_returns_fresh_plain_data(self):
        first = self.ma.load_abi("erc/ERC20")
        second = self.ma.load_abi("erc/ERC20.abi")

        self.assertEqual(first, second)
        self.assertIsNot(first, second)
        self.assertIsInstance(first, list)
        self.assertIsInstance(first[0], dict)
        self.assertEqual(self.ma.loaded_abis(), [])

    def test_legacy_all_abis_returns_fresh_eager_addict_data(self):
        names, first = self.ma.all_abis()
        _, second = self.ma.all_abis()

        self.assertEqual(names, self.ma.ALL_ABIS_NAME)
        self.assertEqual(len(first), 59)
        self.assertIsNot(first, second)
        self.assertIsNot(first.ERC20, second.ERC20)
        self.assertEqual(self.ma.loaded_abis(), [])

    def test_registry_copy_and_to_dict_keep_legacy_shapes(self):
        from addict import Dict

        cached = self.ma.ABIS.ERC20
        shallow = self.ma.ABIS.copy()
        plain = self.ma.ABIS.to_dict()

        self.assertIsInstance(shallow, Dict)
        self.assertIs(shallow.ERC20, cached)
        self.assertIsInstance(plain, dict)
        self.assertNotIsInstance(plain["ERC20"][0], Dict)

    def test_registry_is_read_only_and_path_traversal_is_rejected(self):
        with self.assertRaises(TypeError):
            self.ma.ABIS["ERC20"] = []
        with self.assertRaises(AttributeError):
            self.ma.ABIS.ERC20 = []
        self.assertIn("ERC20", self.ma.ABIS)
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
