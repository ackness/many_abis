import ast
import json
import unittest
from pathlib import Path
from urllib.parse import urlparse

DATA_PATH = (
    Path(__file__).parents[1]
    / "many_abis"
    / "assets"
    / "utils"
    / "chains.json"
)
ASSETS_PATH = DATA_PATH.parents[1]
PACKAGE_PATH = ASSETS_PATH.parent


class ChainDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chains = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    def test_expected_chain_lifecycle(self):
        expected = {
            "base",
            "hyperevm",
            "monad",
            "robinhood",
            "sonic",
            "unichain",
            "xlayer",
        }
        retired = {"fantom", "heco", "kcc", "moonriver", "okx"}

        self.assertTrue(expected.issubset(self.chains))
        self.assertTrue(retired.isdisjoint(self.chains))

    def test_chain_ids_are_unique(self):
        chain_ids = [chain["chain_id"] for chain in self.chains.values()]

        self.assertEqual(len(chain_ids), len(set(chain_ids)))

    def test_xlayer_is_not_legacy_oktchain(self):
        xlayer = self.chains["xlayer"]

        self.assertEqual(xlayer["chain_id"], 196)
        self.assertEqual(xlayer["weth"]["symbol"], "WOKB")
        self.assertEqual(
            xlayer["stable_coins"]["USDC"],
            "0xB6CEceAB302E2E4948951eE7843FC24E92933061",
        )
        self.assertNotIn("USDT", xlayer["stable_coins"])
        self.assertNotIn(
            "0x74b7F16337b8972027F6196A17a631aC6dE26d22",
            xlayer["stable_coins"].values(),
        )
        self.assertEqual(
            xlayer["dex"]["uniswap_v3"]["router_variant"],
            "SwapRouter02",
        )

    def test_required_chain_fields(self):
        required = {
            "chain_id",
            "charts",
            "dex",
            "explorer",
            "name",
            "rpc",
            "stable_coins",
            "weth",
        }

        for slug, chain in self.chains.items():
            with self.subTest(chain=slug):
                self.assertTrue(required.issubset(chain))
                self.assertGreater(len(chain["rpc"]), 0)
                self.assertLessEqual(len(chain["rpc"]), 3)
                self.assertTrue(all(url.startswith("https://") for url in chain["rpc"]))
                self.assertEqual(urlparse(chain["explorer"]).scheme, "https")

    def test_contract_addresses_are_well_formed(self):
        for slug, chain in self.chains.items():
            addresses = [chain["weth"]["address"]]
            addresses.extend(chain["stable_coins"].values())
            addresses.extend(chain.get("test_coins", {}).values())
            for dex in chain["dex"].values():
                addresses.extend(
                    [dex["factory_address"], dex["router_address"]]
                )

            for address in addresses:
                with self.subTest(chain=slug, address=address):
                    self.assertRegex(address, r"^0x[0-9a-fA-F]{40}$")

    def test_typed_dex_entries_have_provenance(self):
        for slug, chain in self.chains.items():
            for dex_slug, dex in chain["dex"].items():
                if "protocol_family" not in dex:
                    continue
                with self.subTest(chain=slug, dex=dex_slug):
                    self.assertIn("protocol_version", dex)
                    self.assertTrue(
                        dex.get("deployment_source", "").startswith("https://")
                    )

    def test_retired_and_unverified_contracts_are_absent(self):
        serialized = json.dumps(self.chains).lower()
        blocked_addresses = {
            # Deprecated Uniswap SwapRouter01 used by the previous config.
            "0xe592427a0aece92de3edee1f18e0157c05861564",
            # Cronos bridged USDC.e previously exposed as native USDC.
            "0xc21223249ca28397b4b6541dffaecc539bff0c59",
            # Optimism retired sUSD and legacy bridged USDT.
            "0x8c6f28f2f1a3c87f0f938b96d27520d9751ec8d9",
            "0x94b008aa00579c1307b0ef2c499ad98a8ce58e58",
            # BSC test token without an official BNB Chain source.
            "0xa83575490d7df4e2f47b7d38ef351a2722ca45b9",
        }
        blocked_dexes = {
            "apeswap",
            "biswap",
            "koffeeswap",
            "mdex",
            "mmf",
            "traderjoe",
            "velodrome_v1",
        }

        for address in blocked_addresses:
            self.assertNotIn(address, serialized)
        for chain in self.chains.values():
            self.assertTrue(blocked_dexes.isdisjoint(chain["dex"]))

    def test_current_native_stablecoin_selection(self):
        self.assertEqual(
            self.chains["cronos"]["stable_coins"],
            {"USDC": "0x3D7F2C478aAfdB65542BCB44bCeeC05849999d2D"},
        )
        self.assertEqual(
            self.chains["optimism"]["stable_coins"]["USDT0"],
            "0x01bFF41798a0BcF287b996046Ca68b395DbC1071",
        )
        self.assertEqual(
            self.chains["avalanche"]["stable_coins"]["USDT"],
            "0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7",
        )
        self.assertEqual(
            self.chains["polygon"]["stable_coins"]["USDT0"],
            "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
        )
        self.assertEqual(
            self.chains["monad"]["stable_coins"]["USDT0"],
            "0xe7cd86e13AC4309349F30B3435a9d337750fC82D",
        )
        self.assertEqual(
            self.chains["unichain"]["stable_coins"]["USDT0"],
            "0x9151434b16b9763660705744891fA906F660EcC5",
        )
        self.assertIn("USDC.binance-peg", self.chains["bsc"]["stable_coins"])
        self.assertIn("USDT.binance-peg", self.chains["bsc"]["stable_coins"])

    def test_swap_router_02_is_used_on_original_v3_deployments(self):
        expected_router = "0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45"
        for slug in ("arbitrum", "eth", "optimism", "polygon"):
            dex = self.chains[slug]["dex"]["uniswap_v3"]
            with self.subTest(chain=slug):
                self.assertEqual(dex["router_address"], expected_router)
                self.assertEqual(dex["router_abi"], "UNISWAP_V3_ROUTER_02")
                self.assertEqual(dex["router_variant"], "SwapRouter02")

    def test_vvs_factory_router_pair(self):
        dex = self.chains["cronos"]["dex"]["vvs_v2"]

        self.assertEqual(
            dex["factory_address"],
            "0x3B44B2a187a7b3824131F8db5a74194D0a42Fc15",
        )
        self.assertEqual(
            dex["router_address"],
            "0x145863Eb42Cf62847A6Ca784e6416C1682b1b2Ae",
        )

    def test_protocol_entries_reference_bundled_abis(self):
        abi_names = {
            "_".join(
                path.relative_to(ASSETS_PATH).with_suffix("").parts[1:]
            ).upper()
            for path in ASSETS_PATH.rglob("*.abi")
        }

        for slug, chain in self.chains.items():
            for dex_slug, dex in chain["dex"].items():
                if "protocol_family" not in dex:
                    continue
                with self.subTest(chain=slug, dex=dex_slug):
                    self.assertIn("factory_abi", dex)
                    self.assertIn("router_abi", dex)
                    self.assertIn(dex["factory_abi"], abi_names)
                    self.assertIn(dex["router_abi"], abi_names)


class AbiDataTests(unittest.TestCase):
    def test_all_abi_files_are_json_arrays(self):
        for path in ASSETS_PATH.rglob("*.abi"):
            with self.subTest(path=path.relative_to(ASSETS_PATH)):
                abi = json.loads(path.read_text(encoding="utf-8"))
                self.assertIsInstance(abi, list)

    def test_swap_router_02_uses_deadline_free_v3_params(self):
        path = ASSETS_PATH / "dex" / "uniswap" / "v3" / "router_02.abi"
        abi = json.loads(path.read_text(encoding="utf-8"))
        exact_input_single = next(
            item for item in abi if item.get("name") == "exactInputSingle"
        )
        param_names = {
            component["name"]
            for component in exact_input_single["inputs"][0]["components"]
        }

        self.assertNotIn("deadline", param_names)
        self.assertIn("amountOutMinimum", param_names)

    def test_slipstream_and_shadow_use_tick_spacing(self):
        paths = (
            ASSETS_PATH
            / "dex"
            / "aerodrome"
            / "slipstream"
            / "v3"
            / "router.abi",
            ASSETS_PATH
            / "dex"
            / "velodrome"
            / "slipstream"
            / "v3"
            / "router.abi",
            ASSETS_PATH / "dex" / "shadow" / "clmm" / "v3" / "router.abi",
        )

        for path in paths:
            abi = json.loads(path.read_text(encoding="utf-8"))
            exact_input_single = next(
                item for item in abi if item.get("name") == "exactInputSingle"
            )
            params = {
                component["name"]: component["type"]
                for component in exact_input_single["inputs"][0]["components"]
            }
            with self.subTest(path=path.relative_to(ASSETS_PATH)):
                self.assertEqual(params["tickSpacing"], "int24")
                self.assertNotIn("fee", params)

    def test_lfj_v2_2_uses_liquidity_book_abi(self):
        path = (
            ASSETS_PATH
            / "dex"
            / "lfj"
            / "liquidity_book"
            / "v2_2"
            / "factory.abi"
        )
        abi = json.loads(path.read_text(encoding="utf-8"))
        function_names = {
            item["name"] for item in abi if item.get("type") == "function"
        }

        self.assertIn("createLBPair", function_names)
        self.assertIn("getPreset", function_names)
        self.assertIn("getQuoteAssetAtIndex", function_names)

    def test_pancake_smart_router_is_not_base_swap_router(self):
        smart_router = json.loads(
            (
                ASSETS_PATH / "dex" / "pancake" / "v3" / "smart_router.abi"
            ).read_text(encoding="utf-8")
        )
        base_router = json.loads(
            (
                ASSETS_PATH / "dex" / "pancake" / "v3" / "router_v3.abi"
            ).read_text(encoding="utf-8")
        )
        smart_functions = {
            item["name"] for item in smart_router if item.get("type") == "function"
        }
        base_functions = {
            item["name"] for item in base_router if item.get("type") == "function"
        }

        self.assertIn("exactInputStableSwap", smart_functions)
        self.assertIn("factoryV2", smart_functions)
        self.assertNotIn("exactInputStableSwap", base_functions)

    def test_explorer_response_parser_does_not_use_eval(self):
        source = (PACKAGE_PATH / "abis.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        eval_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "eval"
        ]

        self.assertEqual(eval_calls, [])


if __name__ == "__main__":
    unittest.main()
