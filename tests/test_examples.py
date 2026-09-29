import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


class ExampleTests(unittest.TestCase):
    def _run(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        environment = dict(os.environ)
        environment.pop("ETHERSCAN_API_KEY", None)
        environment.pop("RPC_URL", None)
        return subprocess.run(
            [sys.executable, *arguments],
            cwd=ROOT,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
            timeout=20,
        )

    def test_quickstart_runs_without_network_or_secrets(self):
        result = self._run("examples/quickstart.py")

        self.assertIn("supported chains:", result.stdout)
        self.assertIn("Base Mainnet", result.stdout)
        self.assertIn("UNISWAP_V3_ROUTER_02", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_catalog_json_is_machine_readable(self):
        result = self._run("examples/inspect_catalog.py", "--chain", "base", "--json")
        payload = json.loads(result.stdout)

        self.assertEqual(payload["chain"]["chain_id"], 8453)
        self.assertEqual(len(payload["dex_contracts"]), 6)
        self.assertEqual(
            {token["configured_symbol"] for token in payload["tokens"]},
            {"USDC", "WETH"},
        )

    def test_network_examples_offer_help_without_network_access(self):
        for script in ("etherscan_lookup.py", "web3_contract.py"):
            with self.subTest(script=script):
                result = self._run("examples/{}".format(script), "--help")
                self.assertIn("usage:", result.stdout.lower())

    def test_all_example_sources_compile(self):
        for path in sorted(EXAMPLES.glob("*.py")):
            with self.subTest(path=path.name):
                compile(path.read_text(encoding="utf-8"), str(path), "exec")


if __name__ == "__main__":
    unittest.main()
