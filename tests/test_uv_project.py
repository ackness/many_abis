import re
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
LOCKFILE = ROOT / "uv.lock"
WORKFLOWS = (
    ROOT / ".github" / "workflows" / "test.yml",
    ROOT / ".github" / "workflows" / "python-publish.yml",
)


class UvProjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configuration = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))

    def test_uv_build_backend_and_static_metadata(self):
        self.assertEqual(
            self.configuration["build-system"]["build-backend"], "uv_build"
        )
        self.assertRegex(
            self.configuration["build-system"]["requires"][0],
            r"^uv_build>=.+,<0\.13$",
        )
        self.assertEqual(self.configuration["project"]["name"], "many-abis")
        self.assertEqual(self.configuration["project"]["version"], "0.5.0")
        self.assertEqual(self.configuration["project"]["requires-python"], ">=3.13")
        self.assertEqual(
            self.configuration["tool"]["uv"]["build-backend"]["module-name"],
            "many_abis",
        )

    def test_legacy_packaging_files_are_removed(self):
        for filename in ("MANIFEST.in", "requirements-dev.txt", "setup.py"):
            with self.subTest(filename=filename):
                self.assertFalse((ROOT / filename).exists())

    def test_lockfile_is_public_and_current_project_is_locked(self):
        lockfile = LOCKFILE.read_text(encoding="utf-8")

        self.assertIn('name = "many-abis"', lockfile)
        self.assertIn('source = { registry = "https://pypi.org/simple" }', lockfile)
        self.assertNotRegex(lockfile, r"https?://[^/\s:@]+:[^/\s@]+@")
        self.assertNotIn("/Users/", lockfile)

    def test_workflows_use_pinned_uv_actions_and_locked_commands(self):
        combined = "\n".join(path.read_text(encoding="utf-8") for path in WORKFLOWS)

        self.assertIn("astral-sh/setup-uv@", combined)
        self.assertIn("uv sync --locked", combined)
        self.assertIn("run: uv publish", combined)
        self.assertNotIn("actions/setup-python@", combined)
        self.assertNotIn("python -m pip", combined)
        self.assertNotIn("python -m build", combined)
        for action_ref in re.findall(r"uses:\s+[^@\s]+@([^\s#]+)", combined):
            with self.subTest(action_ref=action_ref):
                self.assertRegex(action_ref, r"^[0-9a-f]{40}$")


if __name__ == "__main__":
    unittest.main()
