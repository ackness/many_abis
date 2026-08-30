#!/usr/bin/env python3
"""Generate deterministic runtime registry artifacts without network access."""

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
CHAIN_SOURCE_DIR = ROOT / "registry" / "chains"
CHAIN_ORDER_PATH = ROOT / "registry" / "chain-order.json"
ABI_METADATA_PATH = ROOT / "registry" / "abi-metadata.json"
ABI_LEGACY_ALLOWLIST_PATH = ROOT / "registry" / "legacy-abi-allowlist.json"
SCHEMA_DIR = ROOT / "registry" / "schemas"
CHAIN_SOURCE_SCHEMA_PATH = SCHEMA_DIR / "chain-source.schema.json"
ABI_METADATA_SCHEMA_PATH = SCHEMA_DIR / "abi-metadata.schema.json"
ABI_LEGACY_SCHEMA_PATH = SCHEMA_DIR / "legacy-abi-allowlist.schema.json"
ABI_INDEX_SCHEMA_PATH = SCHEMA_DIR / "abi-index.schema.json"
ASSETS_DIR = ROOT / "many_abis" / "assets"
CHAINS_OUTPUT = ASSETS_DIR / "utils" / "chains.json"
ABI_INDEX_OUTPUT = ASSETS_DIR / "abi-index.json"
ABI_STUB_OUTPUT = ROOT / "many_abis" / "abis.pyi"
SUPPORTED_CHAINS_OUTPUT = ROOT / "docs" / "generated" / "supported-chains.md"
ABI_PROVENANCE_OUTPUT = ROOT / "docs" / "generated" / "abi-provenance.md"
THIRD_PARTY_OUTPUT = ROOT / "THIRD_PARTY_NOTICES.md"

ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
REQUIRED_CHAIN_FIELDS = {
    "chain_id",
    "charts",
    "dex",
    "explorer",
    "name",
    "rpc",
    "stable_coins",
    "weth",
}


class RegistryError(ValueError):
    pass


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _json_bytes(value: Any, sort_keys: bool = True) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=sort_keys) + "\n"
    ).encode("utf-8")


def _text_bytes(value: str) -> bytes:
    return value.rstrip().encode("utf-8") + b"\n"


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", dir=str(path.parent)
    )
    try:
        with os.fdopen(descriptor, "wb") as temporary_file:
            temporary_file.write(content)
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RegistryError(message)


def _validate_schema(value: Any, schema_path: Path, location: str) -> None:
    schema = _read_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(value),
        key=lambda error: tuple(str(part) for part in error.path),
    )
    if not errors:
        return
    error = errors[0]
    value_path = ".".join(str(part) for part in error.absolute_path)
    prefix = "{}: ".format(value_path) if value_path else ""
    raise RegistryError("{}: {}{}".format(location, prefix, error.message))


def _validate_address(address: Any, location: str) -> None:
    _require(
        isinstance(address, str) and bool(ADDRESS_RE.fullmatch(address)),
        "{} must be a 20-byte EVM address".format(location),
    )


def _validate_chain(slug: str, source: Mapping[str, Any]) -> Dict[str, Any]:
    _validate_schema(
        source,
        CHAIN_SOURCE_SCHEMA_PATH,
        "registry/chains/{}.json".format(slug),
    )
    _require(source.get("schema_version") == 1, "{}: bad schema version".format(slug))
    _require(source.get("slug") == slug, "{}: slug must match filename".format(slug))
    _require(
        isinstance(source.get("verified_at"), str)
        and bool(DATE_RE.fullmatch(source["verified_at"])),
        "{}: verified_at must be YYYY-MM-DD".format(slug),
    )
    provenance = source.get("provenance")
    _require(isinstance(provenance, dict), "{}: provenance is required".format(slug))
    _require(
        isinstance(provenance.get("chain"), str)
        and provenance["chain"].startswith("https://"),
        "{}: provenance.chain must be an HTTPS URL".format(slug),
    )

    chain = source.get("data")
    _require(isinstance(chain, dict), "{}: data must be an object".format(slug))
    _require(
        REQUIRED_CHAIN_FIELDS.issubset(chain),
        "{}: missing runtime chain fields".format(slug),
    )
    _require(
        isinstance(chain["chain_id"], int) and chain["chain_id"] > 0,
        "{}: chain_id must be positive".format(slug),
    )
    _require(
        isinstance(chain["rpc"], list) and 1 <= len(chain["rpc"]) <= 3,
        "{}: one to three RPC URLs are required".format(slug),
    )
    for rpc in chain["rpc"]:
        _require(
            isinstance(rpc, str) and rpc.startswith("https://"),
            "{}: RPC URLs must use HTTPS".format(slug),
        )

    _validate_address(chain["weth"]["address"], "{}.weth".format(slug))
    for symbol, address in chain["stable_coins"].items():
        _validate_address(address, "{}.stable_coins.{}".format(slug, symbol))
    for symbol, address in chain.get("test_coins", {}).items():
        _validate_address(address, "{}.test_coins.{}".format(slug, symbol))
    for dex_slug, dex in chain["dex"].items():
        _require(isinstance(dex, dict), "{}.dex.{} must be an object".format(slug, dex_slug))
        _validate_address(
            dex.get("factory_address"),
            "{}.dex.{}.factory".format(slug, dex_slug),
        )
        _validate_address(
            dex.get("router_address"),
            "{}.dex.{}.router".format(slug, dex_slug),
        )
        if "protocol_family" in dex:
            for field in (
                "deployment_source",
                "factory_abi",
                "protocol_version",
                "router_abi",
            ):
                _require(
                    bool(dex.get(field)),
                    "{}.dex.{} requires {}".format(slug, dex_slug, field),
                )
    return dict(chain)


def build_chains() -> Dict[str, Any]:
    _require(CHAIN_SOURCE_DIR.is_dir(), "registry/chains is missing")
    order_document = _read_json(CHAIN_ORDER_PATH)
    _require(
        order_document.get("schema_version") == 1,
        "registry/chain-order.json has an unsupported schema version",
    )
    order = order_document.get("chains")
    _require(
        isinstance(order, list) and all(isinstance(value, str) for value in order),
        "registry/chain-order.json must contain a chain slug list",
    )
    _require(len(order) == len(set(order)), "registry/chain-order.json has duplicates")

    discovered = {path.stem: path for path in CHAIN_SOURCE_DIR.glob("*.json")}
    _require(
        set(order) == set(discovered),
        "registry/chain-order.json must list every chain source exactly once",
    )

    chains = {}
    chain_ids = {}
    for slug in order:
        path = discovered[slug]
        source = _read_json(path)
        chain = _validate_chain(slug, source)
        chain_id = chain["chain_id"]
        _require(
            chain_id not in chain_ids,
            "duplicate chain_id {} in {} and {}".format(
                chain_id, chain_ids.get(chain_id), slug
            ),
        )
        chain_ids[chain_id] = slug
        chains[slug] = chain
    _require(bool(chains), "registry/chains contains no chain sources")
    return chains


def _abi_name(path: Path) -> str:
    relative = path.relative_to(ASSETS_DIR).with_suffix("")
    parts = relative.parts[1:]
    _require(bool(parts), "invalid ABI resource path: {}".format(path))
    return "_".join(parts).upper()


def _canonical_type(parameter: Mapping[str, Any]) -> str:
    parameter_type = parameter.get("type", "")
    if not parameter_type.startswith("tuple"):
        return parameter_type
    suffix = parameter_type[len("tuple"):]
    components = parameter.get("components", [])
    return "({}){}".format(
        ",".join(_canonical_type(component) for component in components),
        suffix,
    )


def _abi_signatures(abi: Sequence[Mapping[str, Any]]) -> List[str]:
    signatures = []
    for item in abi:
        item_type = item.get("type")
        if item_type not in {"error", "event", "function"}:
            continue
        signature = "{}:{}({})".format(
            item_type,
            item.get("name", ""),
            ",".join(_canonical_type(value) for value in item.get("inputs", [])),
        )
        signatures.append(signature)
    return sorted(signatures)


def _selector_fingerprint(abi: Sequence[Mapping[str, Any]]) -> str:
    signatures = _abi_signatures(abi)
    payload = "\n".join(sorted(signatures)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_abi_index() -> Tuple[Dict[str, Any], List[str]]:
    metadata_document = _read_json(ABI_METADATA_PATH)
    legacy_document = _read_json(ABI_LEGACY_ALLOWLIST_PATH)
    _validate_schema(
        metadata_document, ABI_METADATA_SCHEMA_PATH, "registry/abi-metadata.json"
    )
    _validate_schema(
        legacy_document,
        ABI_LEGACY_SCHEMA_PATH,
        "registry/legacy-abi-allowlist.json",
    )
    metadata = metadata_document["abis"]
    legacy = legacy_document["abis"]
    overlap = sorted(set(metadata) & set(legacy))
    _require(
        not overlap,
        "ABI names cannot be both audited and legacy: {}".format(", ".join(overlap)),
    )

    entries = {}
    for path in sorted(ASSETS_DIR.rglob("*.abi")):
        abi = _read_json(path)
        _require(isinstance(abi, list), "{} must contain a JSON array".format(path))
        name = _abi_name(path)
        _require(name not in entries, "duplicate ABI name: {}".format(name))
        resource = path.relative_to(ROOT / "many_abis").as_posix()
        canonical = json.dumps(
            abi, ensure_ascii=False, separators=(",", ":"), sort_keys=True
        ).encode("utf-8")
        canonical_sha256 = hashlib.sha256(canonical).hexdigest()
        signatures = _abi_signatures(abi)
        details = metadata.get(name)
        legacy_details = legacy.get(name)
        _require(
            details is not None or legacy_details is not None,
            "{} is not present in audited metadata or the explicit legacy allowlist".format(name),
        )

        if details is not None:
            missing_signatures = sorted(
                set(details["required_signatures"]) - set(signatures)
            )
            _require(
                not missing_signatures,
                "{} is missing required signatures: {}".format(
                    name, ", ".join(missing_signatures)
                ),
            )
            contract_role = details["contract_role"]
            interface_name = details["interface_name"]
            license_data = details["license"]
            provenance = details["provenance"]
            required_signatures = details["required_signatures"]
        else:
            if legacy_details is None:
                raise RegistryError("{} is missing legacy metadata".format(name))
            _require(
                legacy_details["canonical_sha256"] == canonical_sha256,
                "{} legacy ABI changed; audit it instead of updating the allowlist blindly".format(name),
            )
            contract_role = legacy_details["contract_role"]
            interface_name = None
            license_data = {
                "redistribution": "legacy_exception",
                "spdx_expression": "NOASSERTION",
            }
            provenance = {
                "reason": legacy_details["reason"],
                "source_url": None,
                "status": "legacy",
            }
            required_signatures = []

        entry = {
            "canonical_sha256": canonical_sha256,
            "contract_role": contract_role,
            "interface_name": interface_name,
            "item_count": len(abi),
            "license": license_data,
            "provenance": provenance,
            "required_signatures": required_signatures,
            "resource": resource,
            "selector_fingerprint": _selector_fingerprint(abi),
        }
        entries[name] = entry

    unknown_metadata = sorted((set(metadata) | set(legacy)) - set(entries))
    _require(
        not unknown_metadata,
        "ABI registry references missing names: {}".format(", ".join(unknown_metadata)),
    )

    entries_by_hash = {}
    for name, entry in entries.items():
        entries_by_hash.setdefault(entry["canonical_sha256"], []).append(name)
    for names in entries_by_hash.values():
        roles = {entries[name]["contract_role"] for name in names}
        _require(
            len(roles) == 1,
            "identical ABI content cannot have conflicting roles: {}".format(
                ", ".join(sorted(names))
            ),
        )

    result = {"schema_version": 1, "abis": entries}
    _validate_schema(result, ABI_INDEX_SCHEMA_PATH, "generated ABI index")
    return result, sorted(entries)


def validate_abi_references(
    chains: Mapping[str, Any], abi_index: Mapping[str, Any]
) -> None:
    entries = abi_index["abis"]
    for chain_slug, chain in chains.items():
        for dex_slug, dex in chain["dex"].items():
            for role in ("factory", "router"):
                field = role + "_abi"
                if field not in dex:
                    continue
                name = dex[field]
                _require(
                    name in entries,
                    "{}.dex.{} references unknown ABI {}".format(
                        chain_slug, dex_slug, name
                    ),
                )
                _require(
                    entries[name]["contract_role"] == role,
                    "{}.dex.{} uses {} as a {} ABI".format(
                        chain_slug, dex_slug, name, role
                    ),
                )
                _require(
                    entries[name]["provenance"]["status"] == "verified"
                    and entries[name]["license"]["redistribution"] == "allowed",
                    "{}.dex.{} cannot use unaudited ABI {}".format(
                        chain_slug, dex_slug, name
                    ),
                )


def build_abi_stub(names: Sequence[str]) -> str:
    attributes = "\n".join(
        "    @property\n    def {}(self) -> ABI: ...".format(name)
        for name in names
    )
    return """from typing import Any, Dict, Iterator, List, Mapping, Optional, Tuple

ABI = List[Dict[str, Any]]

class _LazyABIRegistry(Mapping[str, ABI]):
{attributes}
    def __getitem__(self, name: str) -> ABI: ...
    def __iter__(self) -> Iterator[str]: ...
    def __len__(self) -> int: ...
    def __contains__(self, name: object) -> bool: ...
    def copy(self) -> Dict[str, ABI]: ...
    def to_dict(self) -> Dict[str, ABI]: ...

ABIS: _LazyABIRegistry
ALL_ABIS_NAME: List[str]

def all_abis() -> Tuple[List[str], Mapping[str, ABI]]: ...
def get_abi(name: str) -> ABI: ...
def clear_abi_cache() -> None: ...
def loaded_abis() -> List[str]: ...
def get_abi_from_address(
    address: str, api_key: str, chain_api: str
) -> Optional[str]: ...
""".format(attributes=attributes)


def build_supported_chains(chains: Mapping[str, Any]) -> str:
    lines = [
        "# Supported chains and DEX deployments",
        "",
        "This file is generated from `registry/chains/*.json`. Do not edit it directly.",
        "",
        "| Slug | Chain ID | Chain | Stablecoins | DEX deployments |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for slug, chain in chains.items():
        lines.append(
            "| `{}` | {} | {} | {} | {} |".format(
                slug,
                chain["chain_id"],
                chain["name"],
                ", ".join("`{}`".format(name) for name in chain["stable_coins"])
                or "—",
                ", ".join("`{}`".format(name) for name in chain["dex"]) or "—",
            )
        )
    return "\n".join(lines) + "\n"


def build_abi_provenance(abi_index: Mapping[str, Any]) -> str:
    lines = [
        "# ABI provenance",
        "",
        "This file is generated from the ABI assets and `registry/abi-metadata.json`.",
        "",
        "| ABI | Role | Items | Canonical SHA-256 | Provenance | License |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    for name, entry in abi_index["abis"].items():
        provenance = entry["provenance"]
        source = provenance.get("source_url")
        source_text = "[source]({})".format(source) if source else provenance["status"]
        license_data = entry["license"]
        lines.append(
            "| `{}` | {} | {} | `{}` | {} | {} ({}) |".format(
                name,
                entry["contract_role"],
                entry["item_count"],
                entry["canonical_sha256"][:16],
                source_text,
                license_data["spdx_expression"],
                license_data["redistribution"],
            )
        )
    return "\n".join(lines) + "\n"


def build_third_party_notices(abi_index: Mapping[str, Any]) -> str:
    known = []
    legacy = []
    for name, entry in abi_index["abis"].items():
        license_data = entry["license"]
        if license_data["redistribution"] == "legacy_exception":
            legacy.append(name)
        else:
            known.append((name, entry))

    lines = [
        "# Third-party notices",
        "",
        "`many-abis` includes ABI data derived from third-party smart-contract projects.",
        "The project license does not replace the upstream terms recorded below.",
        "",
        "## Recorded upstream terms",
        "",
    ]
    for name, entry in known:
        source = entry["provenance"].get("source_url") or "not recorded"
        lines.extend(
            [
                "- `{}`: `{}`; source: {}".format(
                    name, entry["license"]["spdx_expression"], source
                )
            ]
        )
    lines.extend(
        [
            "",
            "## Legacy provenance exceptions",
            "",
            "The following pre-existing ABI files require a future provenance and license",
            "review. No new ABI should use this exception:",
            "",
            ", ".join("`{}`".format(name) for name in legacy),
            "",
        ]
    )
    return "\n".join(lines)


def build_outputs() -> Dict[Path, bytes]:
    chains = build_chains()
    abi_index, names = build_abi_index()
    validate_abi_references(chains, abi_index)
    return {
        CHAINS_OUTPUT: _json_bytes(chains, sort_keys=False),
        ABI_INDEX_OUTPUT: _json_bytes(abi_index),
        ABI_STUB_OUTPUT: _text_bytes(build_abi_stub(names)),
        SUPPORTED_CHAINS_OUTPUT: _text_bytes(build_supported_chains(chains)),
        ABI_PROVENANCE_OUTPUT: _text_bytes(build_abi_provenance(abi_index)),
        THIRD_PARTY_OUTPUT: _text_bytes(build_third_party_notices(abi_index)),
    }


def check_outputs(outputs: Mapping[Path, bytes]) -> List[str]:
    errors = []
    for path, expected in outputs.items():
        if not path.exists():
            errors.append("missing generated file: {}".format(path.relative_to(ROOT)))
        elif path.read_bytes() != expected:
            errors.append("stale generated file: {}".format(path.relative_to(ROOT)))
    return errors


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="write generated files")
    mode.add_argument("--check", action="store_true", help="check committed outputs")
    arguments = parser.parse_args(argv)

    outputs = build_outputs()
    if arguments.write:
        for path, content in outputs.items():
            _atomic_write(path, content)
        print("generated {} registry artifacts".format(len(outputs)))
        return 0

    errors = check_outputs(outputs)
    if errors:
        for error in errors:
            print(error)
        return 1
    print("registry artifacts are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
