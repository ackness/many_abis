#!/usr/bin/env python3
"""Fail unless the checked-out commit, release tag, and package version agree."""

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "many_abis" / "version.py"


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
        raise SystemExit("release tag has an unsupported format: {!r}".format(release_tag))

    match = re.fullmatch(
        r'__version__\s*=\s*"([^"]+)"\s*',
        VERSION_FILE.read_text(encoding="utf-8"),
    )
    if match is None:
        raise SystemExit("many_abis/version.py must contain one literal __version__")

    expected_tag = "v{}".format(match.group(1))
    if release_tag != expected_tag:
        raise SystemExit(
            "release tag {!r} does not match package version {!r}".format(
                release_tag, match.group(1)
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
