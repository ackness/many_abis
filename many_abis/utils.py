import json
from pathlib import PurePosixPath
from typing import Any, Dict, List

try:
    from importlib.resources import files as _resource_files  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover - exercised on Python 3.8
    from importlib_resources import files as _resource_files


_PACKAGE_NAME = "many_abis"
_ASSETS_PREFIX = "assets/"


def _resource(relative_path: str):
    if not isinstance(relative_path, str):
        raise TypeError("Resource path must be a string")

    normalized = relative_path.replace("\\", "/")
    path = PurePosixPath(normalized)
    if (
        not normalized
        or normalized != relative_path
        or path.is_absolute()
        or "." in path.parts
        or ".." in path.parts
    ):
        raise ValueError("Resource path must stay inside the package")

    resource = _resource_files(_PACKAGE_NAME)
    for part in path.parts:
        resource = resource.joinpath(part)
    return resource


def _load_json_resource(relative_path: str) -> Any:
    return json.loads(_resource(relative_path).read_text(encoding="utf-8"))


def load_abi_manifest() -> Dict[str, Any]:
    manifest = _load_json_resource("assets/abi-index.json")
    if (
        not isinstance(manifest, dict)
        or manifest.get("schema_version") != 1
        or not isinstance(manifest.get("abis"), dict)
    ):
        raise ValueError("Unsupported ABI manifest")
    return manifest


def load_abi(name: str) -> List[Dict[str, Any]]:
    """Load one ABI using its legacy path relative to ``assets``.

    ``load_abi("erc/ERC20")`` remains eager and returns a fresh ordinary
    ``list`` on every call. Canonical names are handled by ``get_abi``.
    """
    if not isinstance(name, str):
        raise TypeError("ABI name must be a string")

    normalized = name.replace("\\", "/")
    path = PurePosixPath(normalized)
    if (
        not normalized
        or normalized != name
        or path.is_absolute()
        or "." in path.parts
        or ".." in path.parts
    ):
        raise ValueError("ABI name must be a safe path relative to assets")

    if normalized.endswith(".abi"):
        normalized = normalized[:-4]
    abi = _load_json_resource(_ASSETS_PREFIX + normalized + ".abi")
    if not isinstance(abi, list):
        raise ValueError("ABI resource must contain a JSON array")
    return abi


def load_all_abis() -> Dict[str, List[Dict[str, Any]]]:
    """Eagerly load every ABI using the legacy resource-keyed mapping."""
    result = {}
    for entry in load_abi_manifest()["abis"].values():
        resource_path = entry["resource"]
        legacy_name = "/" + resource_path[len(_ASSETS_PREFIX):-4]
        legacy_path = resource_path[len(_ASSETS_PREFIX):-4]
        result[legacy_name] = load_abi(legacy_path)
    return result


def load_chains() -> Dict[str, Any]:
    return _load_json_resource("assets/utils/chains.json")


def print_all_dex() -> None:
    from .chains import CHAINS

    for name, chain in CHAINS.items():
        print("- {}:".format(name))
        for index, dex in enumerate(chain.dex.values(), start=1):
            print("  - [{}] [{}]({})".format(index, dex.name, dex.website))


def supported_abis() -> List[str]:
    from .abis import ALL_ABIS_NAME

    return list(ALL_ABIS_NAME)
