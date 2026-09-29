import json
import unittest
from copy import deepcopy
from unittest.mock import Mock, patch

import requests
from addict import Dict

import many_abis as ma
from many_abis.constants import ETHERSCAN_V2_API


ADDRESS = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
LEGACY_BSC_API = (
    "https://api.bscscan.com/api?module=contract&action=getabi"
    "&address={contract_address}&apikey={api_key}"
)


class RuntimeMutationSecurityTests(unittest.TestCase):
    def setUp(self):
        ma.clear_abi_cache()

    def test_cached_abi_is_recursively_read_only(self):
        abi = ma.get_abi("ERC20_PERMIT")

        self.assertIsInstance(abi, list)
        self.assertIsInstance(abi[0], Dict)
        self.assertIs(abi, ma.get_abi("ERC20_PERMIT"))
        with self.assertRaisesRegex(TypeError, "read-only"):
            abi.append({"type": "function"})
        with self.assertRaisesRegex(TypeError, "read-only"):
            abi[0]["name"] = "poisoned"
        with self.assertRaisesRegex(TypeError, "read-only"):
            abi[0].name = "poisoned"
        with self.assertRaisesRegex(TypeError, "read-only"):
            abi[0]["outputs"].append({"type": "bytes32"})

        self.assertEqual(
            ma.get_abi("ERC20_PERMIT")[0]["name"], "DOMAIN_SEPARATOR"
        )

    def test_cached_abi_supports_json_and_mutable_deepcopy(self):
        abi = ma.get_abi("ERC20_PERMIT")
        copied = deepcopy(abi)

        self.assertEqual(json.loads(json.dumps(abi)), copied)
        self.assertIsInstance(copied, list)
        self.assertIsInstance(copied[0], Dict)
        copied[0]["name"] = "local-copy"
        copied[0]["outputs"].append({"name": "", "type": "bytes32"})

        self.assertEqual(abi[0]["name"], "DOMAIN_SEPARATOR")
        self.assertEqual(len(abi[0]["outputs"]), 1)

    def test_cached_abi_rejects_every_standard_mutator(self):
        abi = ma.get_abi("ERC20_PERMIT")
        item = abi[0]
        list_mutators = {
            "setitem": lambda: abi.__setitem__(0, {}),
            "delitem": lambda: abi.__delitem__(0),
            "iadd": lambda: abi.__iadd__([]),
            "imul": lambda: abi.__imul__(1),
            "append": lambda: abi.append({}),
            "clear": abi.clear,
            "extend": lambda: abi.extend([]),
            "insert": lambda: abi.insert(0, {}),
            "pop": abi.pop,
            "remove": lambda: abi.remove(item),
            "reverse": abi.reverse,
            "sort": abi.sort,
        }
        dict_mutators = {
            "setitem": lambda: item.__setitem__("name", "poisoned"),
            "delitem": lambda: item.__delitem__("name"),
            "setattr": lambda: item.__setattr__("name", "poisoned"),
            "delattr": lambda: item.__delattr__("name"),
            "ior": lambda: item.__ior__({"name": "poisoned"}),
            "clear": item.clear,
            "pop": lambda: item.pop("name"),
            "popitem": item.popitem,
            "setdefault": lambda: item.setdefault("name", "poisoned"),
            "update": lambda: item.update({"name": "poisoned"}),
        }

        for kind, mutators in (("list", list_mutators), ("dict", dict_mutators)):
            for name, mutate in mutators.items():
                with self.subTest(kind=kind, mutator=name):
                    with self.assertRaisesRegex(TypeError, "read-only"):
                        mutate()

        self.assertEqual(abi[0]["name"], "DOMAIN_SEPARATOR")

    def test_chain_getters_return_independent_recursive_copies(self):
        first = ma.get_chain_by_name("base")
        first["name"] = "poisoned"
        first["rpc"].append("https://attacker.invalid")
        first["dex"].clear()

        second = ma.get_chain_by_id(8453)
        self.assertEqual(second["name"], "Base Mainnet")
        self.assertNotIn("https://attacker.invalid", second["rpc"])
        self.assertIn("uniswap_v3", second["dex"])

        dex = ma.get("base", "dex", "uniswap_v3")
        dex["name"] = "poisoned"
        self.assertEqual(
            ma.get("base", "dex", "uniswap_v3")["name"], "Uniswap V3"
        )

    def test_public_registry_snapshots_are_recursively_read_only(self):
        self.assertIsInstance(ma.SUPPORTED_CHAINS, tuple)
        self.assertEqual(ma.CHAINS.base.name, "Base Mainnet")
        self.assertEqual(json.loads(json.dumps(ma.CHAINS))["base"]["chain_id"], 8453)
        with self.assertRaisesRegex(TypeError, "read-only"):
            ma.CHAINS["base"]["name"] = "poisoned"
        with self.assertRaisesRegex(TypeError, "read-only"):
            ma.CHAINS.base.dex.clear()
        with self.assertRaises(AttributeError):
            ma.SUPPORTED_CHAINS.append("attacker")

        copied = deepcopy(ma.CHAINS)
        copied.base.name = "local-copy"
        copied.base.rpc.append("https://local-copy.invalid")
        self.assertEqual(ma.CHAINS.base.name, "Base Mainnet")
        self.assertNotIn("https://local-copy.invalid", ma.CHAINS.base.rpc)
        self.assertEqual(ma.get_chain("base")["name"], "Base Mainnet")

    def test_public_registry_rejects_standard_mapping_mutators(self):
        base = ma.CHAINS.base
        mutators = {
            "setitem": lambda: base.__setitem__("name", "poisoned"),
            "delitem": lambda: base.__delitem__("name"),
            "setattr": lambda: base.__setattr__("name", "poisoned"),
            "delattr": lambda: base.__delattr__("name"),
            "ior": lambda: base.__ior__({"name": "poisoned"}),
            "clear": base.clear,
            "pop": lambda: base.pop("name"),
            "popitem": base.popitem,
            "setdefault": lambda: base.setdefault("name", "poisoned"),
            "update": lambda: base.update({"name": "poisoned"}),
        }
        for name, mutate in mutators.items():
            with self.subTest(mutator=name):
                with self.assertRaisesRegex(TypeError, "read-only"):
                    mutate()

        self.assertEqual(ma.CHAINS.base.name, "Base Mainnet")


class ExplorerRequestSecurityTests(unittest.TestCase):
    def _mock_session(self):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "status": "1",
            "message": "OK",
            "result": '[{"type":"function","name":"owner"}]',
        }
        session = Mock()
        session.get.return_value = response
        session_context = Mock()
        session_context.__enter__ = Mock(return_value=session)
        session_context.__exit__ = Mock(return_value=False)
        return session_context, session, response

    def test_chain_id_uses_only_etherscan_v2_with_structured_params(self):
        session_context, session, _ = self._mock_session()
        with patch("many_abis.abis.requests.Session", return_value=session_context):
            result = ma.get_abi_from_address(
                ADDRESS, "test-api-key", chain_id=ma.ETHERSCAN_CHAIN_ID.BSC
            )

        self.assertEqual(result, '[{"type":"function","name":"owner"}]')
        session.get.assert_called_once()
        args, kwargs = session.get.call_args
        self.assertEqual(args, (ETHERSCAN_V2_API,))
        self.assertNotIn("test-api-key", args[0])
        self.assertEqual(
            kwargs["params"],
            {
                "chainid": "56",
                "module": "contract",
                "action": "getabi",
                "address": ADDRESS,
                "apikey": "test-api-key",
            },
        )
        self.assertEqual(kwargs["timeout"], (5, 15))
        self.assertFalse(kwargs["allow_redirects"])
        self.assertIn("many-abis/{}".format(ma.__version__), kwargs["headers"]["User-Agent"])

    def test_known_current_and_legacy_templates_are_selectors_only(self):
        for chain_api in (ma.CHAIN_CONTRACT_API.BSC, LEGACY_BSC_API):
            with self.subTest(chain_api=chain_api):
                session_context, session, _ = self._mock_session()
                with patch(
                    "many_abis.abis.requests.Session", return_value=session_context
                ):
                    ma.get_abi_from_address(ADDRESS, "test-api-key", chain_api)

                args, kwargs = session.get.call_args
                self.assertEqual(args, (ETHERSCAN_V2_API,))
                self.assertEqual(kwargs["params"]["chainid"], "56")

    def test_arbitrary_urls_and_invalid_inputs_are_rejected_before_network(self):
        invalid_calls = (
            ((ADDRESS, "key", "https://attacker.invalid/api"), {}),
            ((ADDRESS, "key", "http://api.etherscan.io/v2/api"), {}),
            ((ADDRESS, "key"), {}),
            (("not-an-address", "key"), {"chain_id": 1}),
            (("0x0000000000000000000000000000000000000000", "key"), {"chain_id": 1}),
            ((ADDRESS, "key"), {"chain_id": 0}),
            ((ADDRESS, "key"), {"chain_id": -1}),
            ((ADDRESS, "key"), {"chain_id": 1 << 63}),
            ((ADDRESS, "key"), {"chain_id": True}),
            ((ADDRESS, "secret\nvalue"), {"chain_id": 1}),
            ((ADDRESS, "key", ma.CHAIN_CONTRACT_API.BSC), {"chain_id": 56}),
        )
        with patch("many_abis.abis.requests.Session") as session_type:
            for args, kwargs in invalid_calls:
                with self.subTest(args=args, kwargs=kwargs):
                    with self.assertRaises((TypeError, ValueError)):
                        ma.get_abi_from_address(*args, **kwargs)
            session_type.assert_not_called()

    def test_api_key_is_not_in_network_error_or_output(self):
        session_context, session, _ = self._mock_session()
        session.get.side_effect = requests.Timeout("request failed")
        secret = "not-for-errors"

        with patch("many_abis.abis.requests.Session", return_value=session_context):
            result = ma.get_abi_from_address(ADDRESS, secret, chain_id=1)

        self.assertIsNone(result)

    def test_unsuccessful_or_malformed_explorer_response_returns_none(self):
        for payload in (
            {"status": "0", "message": "NOTOK", "result": "not verified"},
            [],
        ):
            with self.subTest(payload=payload):
                session_context, _, response = self._mock_session()
                response.json.return_value = payload
                with patch(
                    "many_abis.abis.requests.Session", return_value=session_context
                ):
                    self.assertIsNone(
                        ma.get_abi_from_address(ADDRESS, "test-api-key", chain_id=1)
                    )


if __name__ == "__main__":
    unittest.main()
