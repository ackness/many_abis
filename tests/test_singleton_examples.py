"""Offline checks for the singleton-pool example's critical boundaries."""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "examples" / "singleton_pools.py"


def load_example():
    spec = importlib.util.spec_from_file_location("singleton_pools", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SingletonExampleTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec("web3"), "web3.py optional")
    def test_real_swap_logs_decode_with_each_deployed_manager_abi(self):
        from web3 import Web3
        from hexbytes import HexBytes

        example = load_example()
        fixtures = json.loads((ROOT / "tests/fixtures/singleton-swap-logs.json").read_text(encoding="utf-8"))
        for fixture in fixtures:
            with self.subTest(protocol=fixture["protocol"]), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "log.json"
                path.write_text(json.dumps(fixture["raw_log"]), encoding="utf-8")
                args = SimpleNamespace(log_file=path, chain=fixture["chain"], protocol=fixture["protocol"])
                result = example.decode_log(args, Web3, HexBytes)
                self.assertEqual(result["event"], "Swap")
                self.assertEqual(example._jsonable(result["args"]), fixture["expected"])
                invalid = dict(fixture["raw_log"], address="0x" + "00" * 20)
                path.write_text(json.dumps(invalid), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "registered manager"):
                    example.decode_log(args, Web3, HexBytes)

    @unittest.skipUnless(importlib.util.find_spec("web3"), "web3.py optional")
    def test_pool_fixtures_hash_to_observed_ids(self):
        from web3 import Web3
        from hexbytes import HexBytes

        example = load_example()
        fixtures = json.loads((ROOT / "tests/fixtures/singleton-pools.json").read_text(encoding="utf-8"))
        for fixture in fixtures:
            with self.subTest(protocol=fixture["protocol"]):
                key = example._pool_key(fixture["pool_key"], fixture["protocol"], Web3, HexBytes)
                computed = example.pool_id_for_key(Web3(), fixture["protocol"], key)
                self.assertEqual("0x" + computed.hex(), fixture["pool_id"])

    @unittest.skipUnless(importlib.util.find_spec("web3"), "web3.py optional")
    def test_wrong_rpc_chain_is_rejected_before_contract_reads(self):
        example = load_example()
        fake_web3 = MagicMock()
        fake_web3.return_value.is_connected.return_value = True
        fake_web3.return_value.eth.chain_id = 56
        args = SimpleNamespace(chain="base", rpc_url="https://rpc.example", block=None)
        with self.assertRaisesRegex(ValueError, "chain ID"):
            example._rpc(args, fake_web3)
        fake_web3.return_value.eth.contract.assert_not_called()

    def test_help_requires_no_web3_or_network(self):
        environment = dict(os.environ)
        environment["PYTHONPATH"] = str(ROOT)
        for command in ("--help", "state --help", "quote --help", "decode-log --help"):
            with self.subTest(command=command):
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), *command.split()],
                    cwd=ROOT, env=environment, capture_output=True,
                    text=True, timeout=10, check=True,
                )
                self.assertIn("usage:", result.stdout)

    @unittest.skipUnless(importlib.util.find_spec("web3"), "web3.py optional")
    def test_v4_id_uses_struct_abi_encoding_and_all_key_fields(self):
        from web3 import Web3
        from hexbytes import HexBytes

        example = load_example()
        zero = "0x" + "00" * 20
        one = "0x" + "00" * 19 + "01"
        key = example._pool_key(
            {"currency0": zero, "currency1": one, "fee": 3000,
             "tickSpacing": 60, "hooks": zero},
            "uniswap-v4", Web3, HexBytes,
        )
        actual = example.pool_id_for_key(Web3(), "uniswap-v4", key)
        self.assertEqual(
            actual.hex(),
            "9e4ee04ba77ddedb315b9ed859fa005bace0c37b85576fd5f1015e0941519077",
        )
        self.assertNotEqual(
            actual,
            Web3.solidity_keccak(
                ["address", "address", "uint24", "int24", "address"], key
            ),
        )
        changed = (*key[:-1], one)
        self.assertNotEqual(actual, example.pool_id_for_key(Web3(), "uniswap-v4", changed))

    @unittest.skipUnless(importlib.util.find_spec("web3"), "web3.py optional")
    def test_infinity_key_requires_manager_and_distinct_shape(self):
        from web3 import Web3
        from hexbytes import HexBytes

        example = load_example()
        zero = "0x" + "00" * 20
        one = "0x" + "00" * 19 + "01"
        key = {
            "currency0": zero, "currency1": one, "hooks": zero,
            "poolManager": one, "fee": 3000, "parameters": "0x" + "00" * 32,
        }
        normalized = example._pool_key(key, "pancake-infinity-cl", Web3, HexBytes)
        self.assertEqual(len(normalized), 6)
        self.assertEqual(len(example.pool_id_for_key(Web3(), "pancake-infinity-cl", normalized)), 32)
        with self.assertRaisesRegex(ValueError, "exactly"):
            example._pool_key(key, "uniswap-v4", Web3, HexBytes)
        with self.assertRaisesRegex(ValueError, "sort below"):
            example._pool_key({**key, "currency0": one, "currency1": zero},
                              "pancake-infinity-cl", Web3, HexBytes)
        with self.assertRaisesRegex(ValueError, "100000"):
            example._pool_key({**key, "fee": 100001},
                              "pancake-infinity-bin", Web3, HexBytes)

    @unittest.skipUnless(importlib.util.find_spec("web3"), "web3.py optional")
    def test_quote_is_pinned_eth_call_with_explicit_direction(self):
        from web3 import Web3
        from hexbytes import HexBytes

        example = load_example()
        zero = "0x" + "00" * 20
        one = "0x" + "00" * 19 + "01"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "key.json"
            path.write_text(json.dumps({
                "currency0": zero, "currency1": one, "fee": 3000,
                "tickSpacing": 60, "hooks": zero,
            }), encoding="utf-8")
            args = SimpleNamespace(
                amount_in=1234, pool_key_file=path, protocol="uniswap-v4",
                hook_data="0x", chain="base", zero_for_one=False,
                from_address=None,
            )
            contract = MagicMock()
            contract.functions.quoteExactInputSingle.return_value.call.return_value = (987, 123)
            with patch.object(example, "_rpc", return_value=(Web3(), 555)), \
                 patch.object(example, "_record", return_value={"address": one, "abi": "ABI"}), \
                 patch.object(example, "_contract", return_value=contract):
                result = example.quote(args, Web3, HexBytes)
            passed = contract.functions.quoteExactInputSingle.call_args.args[0]
            self.assertEqual(passed[1:], (False, 1234, HexBytes("0x")))
            contract.functions.quoteExactInputSingle.return_value.call.assert_called_once_with(
                {}, block_identifier=555
            )
            self.assertEqual((result["amountOut"], result["block"]), (987, 555))

    @unittest.skipUnless(importlib.util.find_spec("web3"), "web3.py optional")
    def test_bin_state_reads_active_bin_at_one_block(self):
        from web3 import Web3
        from hexbytes import HexBytes

        example = load_example()
        zero = "0x" + "00" * 20
        one = "0x" + "00" * 19 + "01"
        key = (zero, one, zero, one, 3000, HexBytes("0x" + "00" * 32))
        w3 = Web3()
        pool_id = example.pool_id_for_key(w3, "pancake-infinity-bin", key)
        args = SimpleNamespace(
            pool_id="0x" + pool_id.hex(), protocol="pancake-infinity-bin",
            chain="bsc",
        )
        manager = MagicMock()
        manager.functions.getSlot0.return_value.call.return_value = (77, 4, 3000)
        manager.functions.poolIdToPoolKey.return_value.call.return_value = key
        manager.functions.getBin.return_value.call.return_value = (12, 34, 56, 78)
        with patch.object(example, "_rpc", return_value=(w3, 999)), \
             patch.object(example, "_record", return_value={"address": one, "abi": "ABI"}), \
             patch.object(example, "_contract", return_value=manager):
            result = example.read_state(args, Web3, HexBytes)
        self.assertEqual(result["activeBin"], (12, 34, 56, 78))
        manager.functions.getBin.assert_called_once_with(pool_id, 77)
        for name in ("getSlot0", "poolIdToPoolKey", "getBin"):
            getattr(manager.functions, name).return_value.call.assert_called_once_with(
                block_identifier=999
            )

    @unittest.skipUnless(importlib.util.find_spec("web3"), "web3.py optional")
    def test_decodes_complete_rpc_log_without_network(self):
        from eth_utils import event_abi_to_log_topic
        from web3 import Web3
        from hexbytes import HexBytes

        example = load_example()
        manager = "0x" + "12" * 20
        pool_id = HexBytes("0x" + "34" * 32)
        event_abi = {
            "anonymous": False, "type": "event", "name": "Initialized",
            "inputs": [
                {"indexed": True, "name": "id", "type": "bytes32"},
                {"indexed": False, "name": "price", "type": "uint256"},
            ],
        }
        log = {
            "address": manager,
            "topics": ["0x" + event_abi_to_log_topic(event_abi).hex(), "0x" + pool_id.hex()],
            "data": "0x" + Web3().codec.encode(["uint256"], [42]).hex(),
            "blockHash": "0x" + "56" * 32, "blockNumber": "0x1",
            "transactionHash": "0x" + "78" * 32, "transactionIndex": "0x0",
            "logIndex": "0x0", "removed": False,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "log.json"
            path.write_text(json.dumps(log), encoding="utf-8")
            args = SimpleNamespace(
                log_file=path, protocol="uniswap-v4", chain="base",
            )
            with patch.object(example, "_record", return_value={
                "address": manager, "abi": "TEST_ABI"
            }), patch.object(example.ma, "get_abi", return_value=[event_abi]):
                result = example.decode_log(args, Web3, HexBytes)
        self.assertEqual(result["event"], "Initialized")
        self.assertEqual(result["args"], {"id": pool_id, "price": 42})


if __name__ == "__main__":
    unittest.main()
