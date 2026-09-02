#!/usr/bin/env python3
"""Build byte-identical wheel and sdist pairs from clean Git archives."""

import argparse
import copy
import gzip
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Dict


ROOT = Path(__file__).resolve().parents[1]


def _run(*args: str, cwd: Path = ROOT, env: Dict[str, str] | None = None) -> str:
    result = subprocess.run(
        list(args),
        cwd=cwd,
        env=env,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalize_sdist(path: Path, epoch: str) -> None:
    """Remove local account metadata and normalize tar/gzip timestamps."""
    entries = []
    with tarfile.open(path, "r:gz") as archive:
        for member in archive.getmembers():
            payload = None
            if member.isfile():
                extracted = archive.extractfile(member)
                if extracted is None:
                    raise SystemExit("could not read sdist member: {}".format(member.name))
                payload = extracted.read()
            entries.append((copy.copy(member), payload))

    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as raw_stream:
        with gzip.GzipFile(
            filename="",
            mode="wb",
            fileobj=raw_stream,
            mtime=int(epoch),
        ) as gzip_stream:
            with tarfile.open(
                fileobj=gzip_stream,
                mode="w",
                format=tarfile.PAX_FORMAT,
            ) as normalized:
                for member, payload in entries:
                    member.uid = 0
                    member.gid = 0
                    member.uname = "root"
                    member.gname = "root"
                    member.mtime = int(epoch)
                    member.mode = 0o755 if member.isdir() else 0o644
                    member.pax_headers = {}
                    normalized.addfile(
                        member,
                        io.BytesIO(payload) if payload is not None else None,
                    )
    temporary.replace(path)


def _build_once(base: Path, label: str, epoch: str) -> Dict[str, Path]:
    archive = base / "source-{}.tar".format(label)
    source = base / "source-{}".format(label)
    output = base / "dist-{}".format(label)
    source.mkdir()
    output.mkdir()

    subprocess.run(
        ["git", "archive", "--format=tar", "--output", str(archive), "HEAD"],
        cwd=ROOT,
        check=True,
    )
    with tarfile.open(archive) as source_archive:
        source_archive.extractall(source, filter="data")

    environment = dict(os.environ)
    environment["PYTHONHASHSEED"] = "0"
    environment["SOURCE_DATE_EPOCH"] = epoch
    subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            "--outdir",
            str(output),
            str(source),
        ],
        cwd=base,
        env=environment,
        check=True,
    )

    artifacts = {path.name: path for path in sorted(output.iterdir()) if path.is_file()}
    wheels = [name for name in artifacts if name.endswith(".whl")]
    sdists = [name for name in artifacts if name.endswith(".tar.gz")]
    if len(wheels) != 1 or len(sdists) != 1 or len(artifacts) != 2:
        raise SystemExit("build must produce exactly one wheel and one sdist")
    _normalize_sdist(artifacts[sdists[0]], epoch)
    return artifacts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="dist")
    arguments = parser.parse_args()

    dirty = _run("git", "status", "--porcelain=v1", "--untracked-files=all")
    if dirty:
        raise SystemExit("refusing to release from a dirty worktree:\n{}".format(dirty))

    output = Path(arguments.output_dir)
    if not output.is_absolute():
        output = ROOT / output
    if output.exists() and any(output.iterdir()):
        raise SystemExit("output directory is not empty: {}".format(output))

    epoch = _run("git", "show", "-s", "--format=%ct", "HEAD")
    with tempfile.TemporaryDirectory(prefix="many-abis-release-") as temporary:
        base = Path(temporary)
        first = _build_once(base, "a", epoch)
        second = _build_once(base, "b", epoch)

        if set(first) != set(second):
            raise SystemExit("repeated builds produced different artifact names")
        mismatches = [name for name in first if first[name].read_bytes() != second[name].read_bytes()]
        if mismatches:
            raise SystemExit(
                "repeated clean builds were not byte-identical: {}".format(
                    ", ".join(sorted(mismatches))
                )
            )

        output.mkdir(parents=True, exist_ok=True)
        for name, source in first.items():
            destination = output / name
            shutil.copyfile(source, destination)
            print("{}  {}".format(_sha256(destination), name))

    print("reproducible release artifacts written to {}".format(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
