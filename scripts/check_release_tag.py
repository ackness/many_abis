#!/usr/bin/env python3
"""Fail unless the checked-out commit, release tag, and package version agree."""

import re
import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: check_release_tag.py RELEASE_TAG")

    release_tag = sys.argv[1]
    if not re.fullmatch(r"v[0-9A-Za-z][0-9A-Za-z._+-]*", release_tag):
        raise SystemExit(
            "release tag has an unsupported format: {!r}".format(release_tag)
        )

    project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8")).get("project")
    if not isinstance(project, dict) or not isinstance(project.get("version"), str):
        raise SystemExit("pyproject.toml must contain one literal project.version")
    version = project["version"]

    expected_tag = "v{}".format(version)
    if release_tag != expected_tag:
        raise SystemExit(
            "release tag {!r} does not match package version {!r}".format(
                release_tag, version
            )
        )

    head = _git("rev-parse", "HEAD")
    tagged_commit = _git(
        "rev-parse", "--verify", "refs/tags/{}^{{commit}}".format(release_tag)
    )
    if head != tagged_commit:
        raise SystemExit(
            "checked-out commit {} is not release tag {} ({})".format(
                head, release_tag, tagged_commit
            )
        )

    print("release tag verified: {} -> {}".format(release_tag, head))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
