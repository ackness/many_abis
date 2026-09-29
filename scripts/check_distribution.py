#!/usr/bin/env python3
"""Validate PyPI artifacts, including provenance, privacy, and archive safety."""

import argparse
import base64
import csv
import hashlib
import io
import json
import re
import tarfile
import tomllib
import zipfile
from email import policy
from email.parser import BytesParser
from pathlib import Path, PurePosixPath
from typing import Dict, Iterable, Mapping


EXPECTED_LICENSES = {
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "LICENSES/AGPL-3.0.txt",
    "LICENSES/BUSL-1.1.txt",
    "LICENSES/GPL-2.0.txt",
    "LICENSES/GPL-3.0.txt",
    "LICENSES/MIT-Chainlink.txt",
    "LICENSES/MIT-LFJ.txt",
    "LICENSES/MIT-Multicall3.txt",
    "LICENSES/MIT-OpenZeppelin.txt",
    "LICENSES/MIT-Permit2.txt",
    "LICENSES/MIT-Uniswap-V4.txt",
    "LICENSES/README.md",
}
EXPECTED_EXAMPLES = {
    "examples/README.md",
    "examples/etherscan_lookup.py",
    "examples/inspect_catalog.py",
    "examples/quickstart.py",
    "examples/web3_contract.py",
    "examples/singleton_pools.py",
}
MINIMUM_LICENSE_SIZES = {
    "LICENSES/AGPL-3.0.txt": 30_000,
    "LICENSES/BUSL-1.1.txt": 4_000,
    "LICENSES/GPL-2.0.txt": 17_000,
    "LICENSES/GPL-3.0.txt": 30_000,
    "LICENSES/MIT-Chainlink.txt": 900,
    "LICENSES/MIT-LFJ.txt": 900,
    "LICENSES/MIT-Multicall3.txt": 900,
    "LICENSES/MIT-OpenZeppelin.txt": 900,
    "LICENSES/MIT-Permit2.txt": 900,
    "LICENSES/MIT-Uniswap-V4.txt": 900,
}
FORBIDDEN_PATH_PARTS = {
    ".env",
    ".git",
    ".github",
    "__pycache__",
    "legacy-abi-allowlist.json",
    "legacy-abis",
}
FORBIDDEN_CONTENT = (
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(rb"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(rb"\bpypi-[A-Za-z0-9_-]{20,}\b"),
    re.compile(rb"https?://[^/\s:@]+:[^/\s@]+@"),
    re.compile(rb"(?:/Users/|/home/[^/\s]+/|[A-Za-z]:\\\\Users\\\\)"),
    re.compile(rb"ackness8@gmail\.com", re.IGNORECASE),
)
ROOT = Path(__file__).resolve().parents[1]


def _expected_version() -> str:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8")).get(
        "project"
    )
    _require(isinstance(project, dict), "pyproject.toml has no project table")
    version = project.get("version")
    _require(isinstance(version, str), "pyproject.toml has no literal project.version")
    return version


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def _safe_archive_path(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and ".." not in path.parts


def _check_names(names: Iterable[str], label: str) -> None:
    for name in names:
        _require(_safe_archive_path(name), "{} has unsafe path: {}".format(label, name))
        lowered = {part.lower() for part in PurePosixPath(name).parts}
        _require(
            not lowered.intersection(FORBIDDEN_PATH_PARTS),
            "{} contains forbidden path: {}".format(label, name),
        )
        _require(
            not name.endswith((".pyc", ".pyo")), "compiled Python file: {}".format(name)
        )


def _check_content(files: Mapping[str, bytes], label: str) -> None:
    for name, data in files.items():
        if len(data) > 2_000_000:
            continue
        for pattern in FORBIDDEN_CONTENT:
            _require(
                pattern.search(data) is None,
                "{} contains private or credential-like content in {}".format(
                    label, name
                ),
            )
        if name.endswith(".egg-info/SOURCES.txt"):
            _require(
                b"registry/legacy-abis" not in data
                and b"legacy-abi-allowlist.json" not in data,
                "{} source manifest includes quarantined legacy data".format(label),
            )


def _is_package_file(path: PurePosixPath) -> bool:
    if not path.parts or path.parts[0] != "many_abis":
        return False
    if len(path.parts) == 2:
        return path.suffix in {".py", ".pyi"} or path.name == "py.typed"
    if len(path.parts) >= 3 and path.parts[1] == "assets":
        return path.suffix in {".abi", ".json"}
    return False


def _check_wheel_file_set(names: Iterable[str], dist_info: str) -> None:
    allowed_dist_info = {
        "METADATA",
        "RECORD",
        "WHEEL",
        "top_level.txt",
    }
    for name in names:
        if name.endswith("/"):
            continue
        path = PurePosixPath(name)
        if _is_package_file(path):
            continue
        if name.startswith(dist_info + "/licenses/"):
            continue
        if name.startswith(dist_info + "/") and path.name in allowed_dist_info:
            continue
        _require(False, "wheel contains an unexpected file: {}".format(name))


def _check_sdist_file_set(names: Iterable[str], root: str) -> None:
    allowed_root_files = {
        "LICENSE",
        "PKG-INFO",
        "README.md",
        "THIRD_PARTY_NOTICES.md",
        "pyproject.toml",
        "pyproject.toml.orig",
    }
    allowed_egg_info = {
        "PKG-INFO",
        "SOURCES.txt",
        "dependency_links.txt",
        "requires.txt",
        "top_level.txt",
    }
    for name in names:
        relative = name[len(root) :]
        if not relative:
            continue
        path = PurePosixPath(relative)
        if len(path.parts) == 1 and path.name in allowed_root_files:
            continue
        if path.parts[0] == "LICENSES":
            continue
        if path.parts[0] == "examples" and path.suffix in {".md", ".py"}:
            continue
        if _is_package_file(path):
            continue
        if path.parts[0].endswith(".egg-info") and path.name in allowed_egg_info:
            continue
        _require(False, "sdist contains an unexpected file: {}".format(name))


def _license_suffixes(names: Iterable[str], marker: str) -> Dict[str, str]:
    result = {}
    for name in names:
        if marker not in name:
            continue
        suffix = name.split(marker, 1)[1]
        result[suffix] = name
    return result


def _check_abi_manifest(files: Mapping[str, bytes], package_prefix: str) -> None:
    manifest_name = package_prefix + "many_abis/assets/abi-index.json"
    _require(
        manifest_name in files, "ABI manifest is missing: {}".format(manifest_name)
    )
    manifest = json.loads(files[manifest_name].decode("utf-8"))
    entries = manifest.get("abis")
    _require(
        isinstance(entries, dict) and entries, "ABI manifest is empty or malformed"
    )

    resources = set()
    for name, entry in entries.items():
        _require(
            entry.get("provenance", {}).get("status") == "verified",
            "public ABI is not verified: {}".format(name),
        )
        _require(
            entry.get("license", {}).get("spdx_expression") != "NOASSERTION",
            "public ABI has unresolved licensing: {}".format(name),
        )
        resource = entry.get("resource")
        _require(
            isinstance(resource, str) and resource.endswith(".abi"), "bad ABI resource"
        )
        resources.add(package_prefix + "many_abis/" + resource)

    packaged = {
        name
        for name in files
        if name.startswith(package_prefix + "many_abis/") and name.endswith(".abi")
    }
    _require(
        packaged == resources,
        "packaged ABI files do not exactly match the verified manifest",
    )


def _check_metadata(data: bytes) -> None:
    metadata = BytesParser(policy=policy.default).parsebytes(data)
    _require(metadata["Name"] == "many-abis", "unexpected distribution name")
    _require(
        metadata["Version"] == _expected_version(), "unexpected distribution version"
    )
    _require(metadata["Requires-Python"] == ">=3.13", "unexpected Python requirement")
    _require(metadata.get("Author-email") is None, "author email must not be published")
    _require(
        metadata["License-Expression"] == "MIT",
        "unexpected project-code license expression",
    )
    classifiers = set(metadata.get_all("Classifier", []))
    for required in {
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Typing :: Typed",
    }:
        _require(required in classifiers, "missing classifier: {}".format(required))
    description = metadata.get_payload()
    _require(
        "](docs/" not in description,
        "PyPI description contains repository-relative documentation links",
    )


def _check_wheel(path: Path) -> None:
    _require(
        path.name.endswith("-py3-none-any.whl"), "wheel must be platform independent"
    )
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        _check_names(names, "wheel")
        files = {name: archive.read(name) for name in names if not name.endswith("/")}
        _check_content(files, "wheel")

        metadata_names = [
            name for name in names if name.endswith(".dist-info/METADATA")
        ]
        record_names = [name for name in names if name.endswith(".dist-info/RECORD")]
        _require(
            len(metadata_names) == len(record_names) == 1, "wheel metadata is ambiguous"
        )
        dist_info = metadata_names[0].rsplit("/", 1)[0]
        _check_wheel_file_set(names, dist_info)
        _check_metadata(files[metadata_names[0]])
        _check_abi_manifest(files, "")

        record = list(csv.reader(io.StringIO(files[record_names[0]].decode("utf-8"))))
        for name, digest, size in record:
            if not digest:
                continue
            algorithm, encoded = digest.split("=", 1)
            payload = files[name]
            actual = (
                base64.urlsafe_b64encode(hashlib.new(algorithm, payload).digest())
                .rstrip(b"=")
                .decode("ascii")
            )
            _require(actual == encoded, "wheel RECORD digest mismatch: {}".format(name))
            _require(
                len(payload) == int(size), "wheel RECORD size mismatch: {}".format(name)
            )

        licenses = _license_suffixes(files, ".dist-info/licenses/")
        _require(
            set(licenses) == EXPECTED_LICENSES, "wheel license file set is incomplete"
        )
        for suffix, minimum in MINIMUM_LICENSE_SIZES.items():
            _require(
                len(files[licenses[suffix]]) >= minimum,
                "license text is truncated: {}".format(suffix),
            )


def _check_sdist(path: Path) -> None:
    with tarfile.open(path) as archive:
        members = archive.getmembers()
        _require(
            not any(member.issym() or member.islnk() for member in members),
            "sdist must not contain links",
        )
        _require(
            all(
                member.uid == 0
                and member.gid == 0
                and member.uname == "root"
                and member.gname == "root"
                for member in members
            ),
            "sdist tar ownership must be normalized to root:root/0:0",
        )
        names = [member.name for member in members]
        _check_names(names, "sdist")
        files = {
            member.name: archive.extractfile(member).read()
            for member in members
            if member.isfile()
        }
        _check_content(files, "sdist")
        roots = {PurePosixPath(name).parts[0] for name in names}
        _require(len(roots) == 1, "sdist must have one top-level directory")
        root = next(iter(roots)) + "/"
        _require(
            root == "many_abis-{}/".format(_expected_version()),
            "sdist root does not match the package version",
        )
        _check_sdist_file_set(files, root)
        _check_abi_manifest(files, root)

        original_pyproject = root + "pyproject.toml.orig"
        _require(
            files.get(original_pyproject) == (ROOT / "pyproject.toml").read_bytes(),
            "sdist does not preserve the reviewed original pyproject.toml",
        )

        examples = {
            name[len(root) :]
            for name in files
            if name[len(root) :].startswith("examples/")
        }
        _require(
            examples == EXPECTED_EXAMPLES,
            "sdist example file set is incomplete or unexpected",
        )

        licenses = {
            name[len(root) :]: name
            for name in files
            if name[len(root) :] in EXPECTED_LICENSES
        }
        _require(
            set(licenses) == EXPECTED_LICENSES, "sdist license file set is incomplete"
        )
        for suffix, minimum in MINIMUM_LICENSE_SIZES.items():
            _require(
                len(files[licenses[suffix]]) >= minimum,
                "license text is truncated: {}".format(suffix),
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("distribution_directory", type=Path)
    arguments = parser.parse_args()
    directory = arguments.distribution_directory

    wheels = sorted(directory.glob("*.whl"))
    sdists = sorted(directory.glob("*.tar.gz"))
    all_files = sorted(path for path in directory.iterdir() if path.is_file())
    _require(
        len(wheels) == len(sdists) == 1 and len(all_files) == 2,
        "distribution directory must contain exactly one wheel and one sdist",
    )
    _check_wheel(wheels[0])
    _check_sdist(sdists[0])
    print(
        "distribution contents verified: {} {}".format(wheels[0].name, sdists[0].name)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
