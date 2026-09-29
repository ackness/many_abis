import json
import tempfile
import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from scripts import generate_registry as generator
from scripts import refresh_verifications as refresher


class DeploymentSourceTests(unittest.TestCase):
    def setUp(self):
        self.chain = {
            "chain_id": 8453,
            "weth": {"address": "0x" + "1" * 40},
            "stable_coins": {},
            "dex": {},
        }
        self.deployment = {
            "chain": "base",
            "deployment": "uniswap-v4",
            "protocol": "uniswap",
            "protocol_version": "4",
            "deployment_version": "fixture-revision",
            "role": "pool_manager",
            "name": "PoolManager",
            "address": "0x" + "2" * 40,
            "abi": "UNISWAP_V4_POOL_MANAGER",
            "source_url": "https://example.org/deployments",
            "source_reviewed_at": "2026-09-29",
        }

    def load(self, records):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "deployments.json"
            path.write_text(json.dumps({
                "$schema": "../schemas/deployments.schema.json",
                "schema_version": 1,
                "deployments": records,
            }), encoding="utf-8")
            with patch.object(generator, "DEPLOYMENT_SOURCE_DIR", Path(directory)):
                return generator._load_deployments({"base": self.chain})

    def test_explicit_roles_do_not_require_a_factory(self):
        self.assertEqual(self.load([self.deployment]), [self.deployment])

    def test_rejects_unknown_chain_duplicate_role_and_bad_address(self):
        for field, value in (
            ("chain", "unknown"),
            ("address", "0x" + "0" * 40),
            ("address", "0x1234"),
            ("role", "factory"),
            ("abi", None),
            ("deployment_version", ""),
        ):
            record = dict(self.deployment, **{field: value})
            with self.subTest(field=field, value=value):
                with self.assertRaises(generator.RegistryError):
                    self.load([record])
        with self.assertRaisesRegex(generator.RegistryError, "duplicate"):
            self.load([self.deployment, self.deployment])

    def test_duplicate_addresses_preserve_token_checks(self):
        chain = deepcopy(self.chain)
        chain["deployments"] = [
            self.deployment,
            dict(self.deployment, address=chain["weth"]["address"]),
        ]
        targets = refresher._chain_targets(chain)
        self.assertEqual(len(targets), 2)
        self.assertTrue(targets[chain["weth"]["address"]][1])
        self.assertFalse(targets[self.deployment["address"]][1])

    def test_rejects_abis_swapped_between_similar_roles(self):
        records = (
            dict(self.deployment, role="state_view", abi="UNISWAP_V4_QUOTER"),
            dict(self.deployment, deployment="pancake-infinity-cl",
                 abi="PANCAKE_INFINITY_BIN_POOL_MANAGER"),
            dict(self.deployment, deployment="unknown-protocol"),
        )
        for record in records:
            with self.subTest(record=record):
                with self.assertRaisesRegex(generator.RegistryError, "binding"):
                    self.load([record])

    def test_collect_rejects_unregistered_subset_before_network(self):
        with patch.object(refresher.requests, "Session") as session:
            with self.assertRaises(refresher.VerificationError):
                refresher._collect_chain(
                    "base", self.chain, "latest", 1, ["0x" + "3" * 40]
                )
            session.assert_not_called()

    def test_missing_only_preserves_existing_snapshot_and_only_queries_new_address(self):
        chain = dict(self.chain, deployments=[self.deployment])
        old_key = "base:" + self.chain["weth"]["address"]
        new_key = "base:" + self.deployment["address"]
        old = {"chain": "base", "block_number": 42}
        new = {"chain": "base", "block_number": 99}
        with patch.object(refresher, "_load_chains", return_value={"base": chain}), \
             patch.object(refresher, "_read_json", return_value={"snapshots": {old_key: old}}), \
             patch.object(refresher, "_collect_chain", return_value=({new_key: new}, "https://rpc.example", 99)) as collect, \
             patch.object(refresher, "_write_json") as write, redirect_stdout(StringIO()):
            self.assertEqual(refresher.main(["--chain", "base", "--missing-only", "--write"]), 0)
        self.assertEqual(collect.call_args.args[-1], [self.deployment["address"]])
        self.assertEqual(write.call_args.args[1]["snapshots"], {old_key: old, new_key: new})


if __name__ == "__main__":
    unittest.main()
