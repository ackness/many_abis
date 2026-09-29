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
from urllib.parse import urlsplit

from eth_utils import is_checksum_address
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CHAIN_SOURCE_DIR = ROOT / "registry" / "chains"
DEPLOYMENT_SOURCE_DIR = ROOT / "registry" / "deployments"
CHAIN_ORDER_PATH = ROOT / "registry" / "chain-order.json"
ABI_METADATA_PATH = ROOT / "registry" / "abi-metadata.json"
ABI_LEGACY_ALLOWLIST_PATH = ROOT / "registry" / "legacy-abi-allowlist.json"
LEGACY_ABI_DIR = ROOT / "registry" / "legacy-abis"
TOKEN_POLICIES_PATH = ROOT / "registry" / "token-policies.json"
VERIFICATION_SNAPSHOTS_PATH = ROOT / "registry" / "verification-snapshots.json"
SCHEMA_DIR = ROOT / "registry" / "schemas"
CHAIN_SOURCE_SCHEMA_PATH = SCHEMA_DIR / "chain-source.schema.json"
ABI_METADATA_SCHEMA_PATH = SCHEMA_DIR / "abi-metadata.schema.json"
ABI_LEGACY_SCHEMA_PATH = SCHEMA_DIR / "legacy-abi-allowlist.schema.json"
ABI_INDEX_SCHEMA_PATH = SCHEMA_DIR / "abi-index.schema.json"
TOKEN_POLICIES_SCHEMA_PATH = SCHEMA_DIR / "token-policies.schema.json"
VERIFICATION_SNAPSHOTS_SCHEMA_PATH = (
    SCHEMA_DIR / "verification-snapshots.schema.json"
)
CONTRACT_INDEX_SCHEMA_PATH = SCHEMA_DIR / "contract-index.schema.json"
DEPLOYMENTS_SCHEMA_PATH = SCHEMA_DIR / "deployments.schema.json"
TOKEN_INDEX_SCHEMA_PATH = SCHEMA_DIR / "token-index.schema.json"
ASSETS_DIR = ROOT / "many_abis" / "assets"
CHAINS_OUTPUT = ASSETS_DIR / "utils" / "chains.json"
ABI_INDEX_OUTPUT = ASSETS_DIR / "abi-index.json"
CONTRACT_INDEX_OUTPUT = ASSETS_DIR / "contract-index.json"
TOKEN_INDEX_OUTPUT = ASSETS_DIR / "token-index.json"
VERIFICATION_SNAPSHOTS_OUTPUT = ASSETS_DIR / "verification-snapshots.json"
ABI_STUB_OUTPUT = ROOT / "many_abis" / "abis.pyi"
SUPPORTED_CHAINS_OUTPUT = ROOT / "docs" / "generated" / "supported-chains.md"
ABI_PROVENANCE_OUTPUT = ROOT / "docs" / "generated" / "abi-provenance.md"
CONTRACT_CATALOG_DOC_OUTPUT = ROOT / "docs" / "generated" / "contract-catalog.md"
TOKEN_CATALOG_DOC_OUTPUT = ROOT / "docs" / "generated" / "token-catalog.md"
THIRD_PARTY_OUTPUT = ROOT / "THIRD_PARTY_NOTICES.md"

ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID_PART_RE = re.compile(r"[^a-z0-9]+")
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
DEPLOYMENT_ABI_ROLES = {
    "pool_manager": "pool",
    "state_view": "utility",
    "quoter": "utility",
    "position_manager": "other",
    "router": "router",
    "permit2": "token",
    "vault": "vault",
}
# Approved bindings prevent interfaces with the same broad ABI role (for example,
# StateView/Quoter or CL/Bin managers) from being accidentally interchanged.
DEPLOYMENT_ABIS = {
    "uniswap-v4": {
        "pool_manager": "UNISWAP_V4_POOL_MANAGER",
        "state_view": "UNISWAP_V4_STATE_VIEW",
        "quoter": "UNISWAP_V4_QUOTER",
        "position_manager": "UNISWAP_V4_POSITION_MANAGER",
    },
    "uniswap-universal-router-2-1-2": {"router": "UNISWAP_UNIVERSAL_ROUTER_V2_1_2"},
    "uniswap-permit2": {"permit2": "UNISWAP_PERMIT2"},
    "pancake-infinity-cl": {
        "pool_manager": "PANCAKE_INFINITY_CL_POOL_MANAGER",
        "quoter": "PANCAKE_INFINITY_CL_QUOTER",
        "position_manager": "PANCAKE_INFINITY_CL_POSITION_MANAGER",
    },
    "pancake-infinity-bin": {
        "pool_manager": "PANCAKE_INFINITY_BIN_POOL_MANAGER",
        "quoter": "PANCAKE_INFINITY_BIN_QUOTER",
        "position_manager": "PANCAKE_INFINITY_BIN_POSITION_MANAGER",
    },
    "pancake-infinity": {
        "vault": "PANCAKE_INFINITY_VAULT",
        "router": "PANCAKE_INFINITY_UNIVERSAL_ROUTER",
        "permit2": "UNISWAP_PERMIT2",
    },
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
    _require(
        int(address, 16) != 0,
        "{} must not be the zero address".format(location),
    )
    body = address[2:]
    mixed_case = body.lower() != body and body.upper() != body
    _require(
        not mixed_case or is_checksum_address(address),
        "{} has an invalid EIP-55 checksum".format(location),
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
        parsed_rpc = urlsplit(rpc) if isinstance(rpc, str) else None
        _require(
            parsed_rpc is not None
            and parsed_rpc.scheme == "https"
            and bool(parsed_rpc.hostname)
            and parsed_rpc.username is None
            and parsed_rpc.password is None
            and "@" not in parsed_rpc.netloc
            and not parsed_rpc.query
            and not parsed_rpc.fragment,
            "{}: RPC URLs must use HTTPS without credentials, query, or fragment".format(
                slug
            ),
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


def _id_part(value: str) -> str:
    normalized = ID_PART_RE.sub("-", value.lower()).strip("-")
    _require(bool(normalized), "registry identifier parts cannot be empty")
    return normalized


def _verification_id(chain: str, address: str) -> str:
    return "{}:{}".format(chain, address.lower())


def _load_chain_sources(chains: Mapping[str, Any]) -> Dict[str, Any]:
    sources = {}
    for slug in chains:
        source = _read_json(CHAIN_SOURCE_DIR / (slug + ".json"))
        _require(source.get("slug") == slug, "{} source slug changed".format(slug))
        sources[slug] = source
    return sources


def _add_contract(
    contracts: Dict[str, Any], contract_id: str, record: Mapping[str, Any]
) -> None:
    _require(contract_id not in contracts, "duplicate contract id: {}".format(contract_id))
    value = dict(record)
    value["contract_id"] = contract_id
    contracts[contract_id] = value


def _load_deployments(chains: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Read explicit deployments without changing the legacy chain data shape."""
    deployments = []
    seen = set()
    for path in sorted(DEPLOYMENT_SOURCE_DIR.glob("*.json")):
        document = _read_json(path)
        _validate_schema(document, DEPLOYMENTS_SCHEMA_PATH, path.name)
        for record in document["deployments"]:
            location = "{}:{}:{}".format(
                record["chain"], record["deployment"], record["role"]
            )
            _require(record["chain"] in chains, "{}: unknown chain".format(location))
            _validate_address(record["address"], location)
            expected_abi = DEPLOYMENT_ABIS.get(record["deployment"], {}).get(record["role"])
            _require(
                expected_abi is not None and record["abi"] == expected_abi,
                "{}: unapproved deployment/role/ABI binding".format(location),
            )
            _require(location not in seen, "duplicate deployment: {}".format(location))
            seen.add(location)
            deployments.append(record)
    return deployments


def _build_contract_records(
    chains: Mapping[str, Any], token_policies: Mapping[str, Any]
) -> Dict[str, Any]:
    sources = _load_chain_sources(chains)
    contracts = {}
    for chain_slug, chain in chains.items():
        source = sources[chain_slug]
        common = {
            "chain": chain_slug,
            "chain_id": chain["chain_id"],
            "source_reviewed_at": source["verified_at"],
        }
        for dex_slug, dex in chain["dex"].items():
            protocol = dex.get("protocol_family") or dex_slug
            for role in ("factory", "router"):
                abi_name = dex.get(role + "_abi")
                provenance_status = (
                    "verified"
                    if dex.get("deployment_source") and abi_name
                    else "legacy_unverified"
                )
                contract_id = "{}:dex:{}:{}".format(
                    chain_slug, _id_part(dex_slug), role
                )
                _add_contract(
                    contracts,
                    contract_id,
                    dict(
                        common,
                        abi=abi_name,
                        address=dex[role + "_address"],
                        name="{} {}".format(dex["name"], role.title()),
                        protocol=protocol,
                        protocol_version=dex.get("protocol_version"),
                        provenance_status=provenance_status,
                        role=role,
                        source_url=dex.get("deployment_source"),
                        verification_id=_verification_id(
                            chain_slug, dex[role + "_address"]
                        ),
                    ),
                )

        token_groups = (
            ("stable_coins", "stablecoin"),
            ("test_coins", "test_token"),
        )
        for field, role in token_groups:
            for symbol, address in chain.get(field, {}).items():
                token_id = "{}:{}".format(chain_slug, symbol)
                policy = token_policies.get(token_id, {})
                evidence_url = policy.get("evidence_url")
                contract_id = "{}:token:{}:{}".format(
                    chain_slug, role.replace("_", "-"), _id_part(symbol)
                )
                _add_contract(
                    contracts,
                    contract_id,
                    dict(
                        common,
                        abi=None,
                        address=address,
                        name=symbol,
                        protocol=None,
                        protocol_version=None,
                        provenance_status=(
                            "verified" if evidence_url else "legacy_unverified"
                        ),
                        role=role,
                        source_url=evidence_url,
                        verification_id=_verification_id(chain_slug, address),
                    ),
                )

        wrapped = chain["weth"]
        wrapped_id = "{}:token:wrapped-native:{}".format(
            chain_slug, _id_part(wrapped["symbol"])
        )
        _add_contract(
            contracts,
            wrapped_id,
            dict(
                common,
                abi=None,
                address=wrapped["address"],
                name=wrapped["name"],
                protocol=None,
                protocol_version=None,
                provenance_status="verified",
                role="wrapped_native",
                source_url=source["provenance"]["chain"],
                verification_id=_verification_id(chain_slug, wrapped["address"]),
            ),
        )
    for deployment in _load_deployments(chains):
        slug = deployment["chain"]
        contract_id = "{}:dex:{}:{}".format(
            slug, deployment["deployment"], deployment["role"]
        )
        record = {
            key: value for key, value in deployment.items() if key != "deployment"
        }
        record.update(
            chain_id=chains[slug]["chain_id"],
            provenance_status="verified",
            verification_id=_verification_id(slug, deployment["address"]),
        )
        _add_contract(contracts, contract_id, record)
    return contracts


def _default_token_origin(role: str) -> str:
    if role == "wrapped_native":
        return "wrapped_native"
    if role == "test_token":
        return "test"
    return "unknown"


def _validate_contract_snapshot(
    contract_id: str,
    contract: Mapping[str, Any],
    snapshot: Mapping[str, Any],
    chain: Mapping[str, Any],
) -> None:
    _require(
        snapshot["rpc_url"] in chain["rpc"],
        "{} snapshot RPC is not registered for its chain".format(contract_id),
    )
    _validate_address(
        snapshot["address"], "{}.snapshot.address".format(contract_id)
    )
    _require(
        snapshot["chain"] == contract["chain"]
        and snapshot["chain_id"] == contract["chain_id"]
        and snapshot["address"].lower() == contract["address"].lower(),
        "{} verification identity does not match its contract".format(contract_id),
    )
    implementation = snapshot["eip1967"]["implementation"]
    implementation_hash = snapshot["eip1967"][
        "implementation_code_keccak256"
    ]
    for slot_name in ("admin", "beacon", "implementation"):
        slot_address = snapshot["eip1967"][slot_name]
        if slot_address is not None:
            _validate_address(
                slot_address,
                "{}.snapshot.eip1967.{}".format(contract_id, slot_name),
            )
    _require(
        (implementation is None) == (implementation_hash is None),
        "{} implementation and code hash must appear together".format(
            contract_id
        ),
    )


def build_catalogs(
    chains: Mapping[str, Any], abi_index: Mapping[str, Any]
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    token_policy_document = _read_json(TOKEN_POLICIES_PATH)
    snapshot_document = _read_json(VERIFICATION_SNAPSHOTS_PATH)
    _validate_schema(
        token_policy_document,
        TOKEN_POLICIES_SCHEMA_PATH,
        "registry/token-policies.json",
    )
    _validate_schema(
        snapshot_document,
        VERIFICATION_SNAPSHOTS_SCHEMA_PATH,
        "registry/verification-snapshots.json",
    )
    token_policies = token_policy_document["tokens"]
    snapshots = snapshot_document["snapshots"]
    contracts = _build_contract_records(chains, token_policies)

    expected_verifications = {
        record["verification_id"] for record in contracts.values()
    }
    _require(
        set(snapshots) == expected_verifications,
        "verification snapshots must exactly cover every registered chain address",
    )

    abi_entries = abi_index["abis"]
    for contract_id, contract in contracts.items():
        abi_name = contract["abi"]
        if abi_name is not None:
            _require(
                abi_name in abi_entries,
                "{} references unknown ABI {}".format(contract_id, abi_name),
            )
        if "deployment_version" in contract:
            _require(abi_name is not None, "{} requires an ABI".format(contract_id))
            expected_role = DEPLOYMENT_ABI_ROLES[contract["role"]]
            _require(
                abi_entries[abi_name]["contract_role"] == expected_role,
                "{} requires a {} ABI".format(contract_id, expected_role),
            )
        requires_abi = contract["role"] in {"factory", "router"} or "deployment_version" in contract
        expected_provenance_status = (
            "verified"
            if contract["source_url"] and (abi_name is not None or not requires_abi)
            else "legacy_unverified"
        )
        _require(
            contract["provenance_status"] == expected_provenance_status,
            "{} has inconsistent provenance_status".format(contract_id),
        )
        snapshot = snapshots[contract["verification_id"]]
        _validate_contract_snapshot(
            contract_id,
            contract,
            snapshot,
            chains[contract["chain"]],
        )

    tokens = {}
    token_contracts = {
        contract_id: contract
        for contract_id, contract in contracts.items()
        if contract["role"] in {"stablecoin", "test_token", "wrapped_native"}
    }
    token_lookup_keys = set()
    for contract_id, contract in token_contracts.items():
        configured_symbol = contract["name"]
        name = None
        if contract["role"] == "wrapped_native":
            chain = chains[contract["chain"]]
            configured_symbol = chain["weth"]["symbol"]
            name = chain["weth"]["name"]
        token_id = "{}:{}".format(contract["chain"], configured_symbol)
        _require(token_id not in tokens, "duplicate token id: {}".format(token_id))
        lookup_key = (contract["chain"], configured_symbol.casefold())
        _require(
            lookup_key not in token_lookup_keys,
            "duplicate case-insensitive token symbol: {}".format(token_id),
        )
        token_lookup_keys.add(lookup_key)
        snapshot = snapshots[contract["verification_id"]]
        observed = snapshot["token_metadata"]
        _require(
            observed is not None,
            "{} must include on-chain token metadata".format(contract_id),
        )
        policy = token_policies.get(token_id, {})
        tokens[token_id] = {
            "address": contract["address"],
            "chain": contract["chain"],
            "chain_id": contract["chain_id"],
            "configured_symbol": configured_symbol,
            "decimals": observed["decimals"],
            "evidence_url": policy.get("evidence_url") or contract["source_url"],
            "name": name,
            "observed_symbol": observed["symbol"],
            "origin": policy.get("origin")
            or _default_token_origin(contract["role"]),
            "role": contract["role"],
            "token_id": token_id,
            "verification_id": contract["verification_id"],
        }

    unknown_policies = sorted(set(token_policies) - set(tokens))
    _require(
        not unknown_policies,
        "token policies reference unknown tokens: {}".format(
            ", ".join(unknown_policies)
        ),
    )

    contract_index = {"schema_version": 1, "contracts": contracts}
    token_index = {"schema_version": 1, "tokens": tokens}
    _validate_schema(
        contract_index, CONTRACT_INDEX_SCHEMA_PATH, "generated contract index"
    )
    _validate_schema(token_index, TOKEN_INDEX_SCHEMA_PATH, "generated token index")
    runtime_snapshots = {
        "schema_version": 1,
        "snapshots": snapshots,
    }
    return contract_index, token_index, runtime_snapshots


def _abi_name(path: Path, root: Path = ASSETS_DIR) -> str:
    relative = path.relative_to(root).with_suffix("")
    parts = relative.parts[1:]
    _require(bool(parts), "invalid ABI resource path: {}".format(path))
    return "_".join(parts).upper()


def _canonical_abi_sha256(abi: Sequence[Mapping[str, Any]]) -> str:
    canonical = json.dumps(
        abi, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


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

    _require(LEGACY_ABI_DIR.is_dir(), "registry/legacy-abis is missing")
    quarantined = {}
    for path in sorted(LEGACY_ABI_DIR.rglob("*.abi")):
        abi = _read_json(path)
        _require(isinstance(abi, list), "{} must contain a JSON array".format(path))
        name = _abi_name(path, LEGACY_ABI_DIR)
        _require(
            name not in quarantined,
            "duplicate quarantined ABI name: {}".format(name),
        )
        details = legacy.get(name)
        _require(
            details is not None,
            "{} is not present in the legacy ABI allowlist".format(name),
        )
        canonical_sha256 = _canonical_abi_sha256(abi)
        _require(
            details["canonical_sha256"] == canonical_sha256,
            "{} quarantined ABI changed; audit it instead of updating the allowlist blindly".format(
                name
            ),
        )
        quarantined[name] = canonical_sha256
    missing_quarantine = sorted(set(legacy) - set(quarantined))
    _require(
        not missing_quarantine,
        "legacy ABI registry references missing quarantine files: {}".format(
            ", ".join(missing_quarantine)
        ),
    )

    entries = {}
    for path in sorted(ASSETS_DIR.rglob("*.abi")):
        abi = _read_json(path)
        _require(isinstance(abi, list), "{} must contain a JSON array".format(path))
        name = _abi_name(path)
        _require(name not in entries, "duplicate ABI name: {}".format(name))
        _require(
            name not in legacy,
            "{} is a quarantined legacy ABI and cannot be distributed".format(name),
        )
        resource = path.relative_to(ROOT / "many_abis").as_posix()
        canonical_sha256 = _canonical_abi_sha256(abi)
        signatures = _abi_signatures(abi)
        details = metadata.get(name)
        _require(
            details is not None,
            "{} is not present in audited ABI metadata".format(name),
        )

        _require(
            details["canonical_sha256"] == canonical_sha256,
            "{} verified ABI content does not match canonical_sha256".format(name),
        )
        missing_signatures = sorted(
            set(details["required_signatures"]) - set(signatures)
        )
        _require(
            not missing_signatures,
            "{} is missing required signatures: {}".format(
                name, ", ".join(missing_signatures)
            ),
        )

        entry = {
            "canonical_sha256": canonical_sha256,
            "contract_role": details["contract_role"],
            "interface_name": details["interface_name"],
            "item_count": len(abi),
            "license": details["license"],
            "provenance": details["provenance"],
            "required_signatures": details["required_signatures"],
            "resource": resource,
            "selector_fingerprint": _selector_fingerprint(abi),
        }
        entries[name] = entry

    unknown_metadata = sorted(set(metadata) - set(entries))
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
    return """from typing import Any, Dict, Iterator, List, Mapping, Optional, Tuple, Union

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
def get_abi_info(name: str) -> Dict[str, Any]: ...
def find_abis(
    contract_role: Optional[str] = ...,
    interface_name: Optional[str] = ...,
    provenance_status: Optional[str] = ...,
) -> List[str]: ...
def clear_abi_cache() -> None: ...
def loaded_abis() -> List[str]: ...
def get_abi_from_address(
    address: str,
    api_key: str,
    chain_api: Optional[Union[str, int]] = ...,
    *,
    chain_id: Optional[int] = ...,
) -> Optional[str]: ...
""".format(attributes=attributes)


def build_supported_chains(chains: Mapping[str, Any]) -> str:
    deployments = _load_deployments(chains)
    lines = [
        "# Supported chains and DEX deployments",
        "",
        "Generated from `registry/chains/*.json` and `registry/deployments/*.json`.",
        "Do not edit it directly. Singleton components are available in the contract catalog.",
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
                ", ".join(
                    "`{}`".format(name) for name in sorted(
                        set(chain["dex"]) | {
                            record["deployment"] for record in deployments
                            if record["chain"] == slug
                        }
                    )
                ) or "—",
            )
        )
    return "\n".join(lines) + "\n"


def build_abi_provenance(abi_index: Mapping[str, Any]) -> str:
    lines = [
        "# ABI provenance",
        "",
        "This file is generated from the ABI assets and `registry/abi-metadata.json`.",
        "Only verified ABIs are distributed. Legacy ABI audit records and content are",
        "quarantined under `registry/` and are unavailable through the runtime API.",
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


def build_contract_catalog(
    contract_index: Mapping[str, Any], snapshot_index: Mapping[str, Any]
) -> str:
    contracts = contract_index["contracts"]
    snapshots = snapshot_index["snapshots"]
    chains = sorted({record["chain"] for record in contracts.values()})
    lines = [
        "# Contract verification catalog",
        "",
        "This file is generated from the chain registry and pinned on-chain",
        "verification snapshots. A code hash proves observed bytecode identity at",
        "one block; it is not a security audit or a promise that mutable contracts",
        "will keep the same implementation. Public RPC endpoints are not guaranteed",
        "to retain archive state, so long-term replay of a snapshot may be unavailable.",
        "",
        "| Chain | Logical contracts | Unique addresses | EIP-1967 implementations | Snapshot block |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for chain in chains:
        chain_contracts = [
            record for record in contracts.values() if record["chain"] == chain
        ]
        verification_ids = {
            record["verification_id"] for record in chain_contracts
        }
        chain_snapshots = [snapshots[key] for key in verification_ids]
        blocks = sorted({snapshot["block_number"] for snapshot in chain_snapshots})
        proxy_count = sum(
            snapshot["eip1967"]["implementation"] is not None
            or snapshot["eip1967"]["beacon"] is not None
            for snapshot in chain_snapshots
        )
        block_text = ", ".join(str(block) for block in blocks)
        lines.append(
            "| `{}` | {} | {} | {} | {} |".format(
                chain,
                len(chain_contracts),
                len(verification_ids),
                proxy_count,
                block_text,
            )
        )
    return "\n".join(lines) + "\n"


def build_token_catalog(token_index: Mapping[str, Any]) -> str:
    lines = [
        "# Token catalog",
        "",
        "This file is generated from current chain defaults, conservative origin",
        "policies, and on-chain metadata observed at the linked verification",
        "snapshot. `unknown` means the registry does not make an origin claim.",
        "",
        "| Chain | Configured symbol | On-chain symbol | Decimals | Origin | Address | Evidence |",
        "| --- | --- | --- | ---: | --- | --- | --- |",
    ]
    for token in token_index["tokens"].values():
        evidence = token["evidence_url"]
        evidence_text = "[source]({})".format(evidence) if evidence else "—"
        lines.append(
            "| `{}` | `{}` | `{}` | {} | {} | `{}` | {} |".format(
                token["chain"],
                token["configured_symbol"],
                token["observed_symbol"],
                token["decimals"],
                token["origin"],
                token["address"],
                evidence_text,
            )
        )
    return "\n".join(lines) + "\n"


def build_third_party_notices(
    abi_index: Mapping[str, Any], quarantined_names: Sequence[str]
) -> str:
    known = []
    for name, entry in abi_index["abis"].items():
        known.append((name, entry))

    lines = [
        "# Third-party notices",
        "",
        "`many-abis` includes ABI data derived from third-party smart-contract projects.",
        "The project license does not replace the upstream terms recorded below.",
        "Full upstream/standard license texts and copyright notices are bundled under",
        "`LICENSES/`; including them is not a legal or smart-contract security conclusion.",
        "",
        "## Recorded upstream terms",
        "",
    ]
    for name, entry in known:
        source = entry["provenance"].get("source_url") or "not recorded"
        evidence = entry["license"].get("evidence_url") or "not recorded"
        lines.extend(
            [
                "- `{}`: `{}`; ABI source: {}; license evidence: {}".format(
                    name,
                    entry["license"]["spdx_expression"],
                    source,
                    evidence,
                )
            ]
        )
    lines.extend(
        [
            "",
            "## Quarantined legacy ABI records",
            "",
            "The following pre-existing ABI files still require provenance and license",
            "review. Their content is retained under `registry/legacy-abis/` for audit",
            "history only; it is not included in the Python package or runtime ABI index:",
            "",
            ", ".join("`{}`".format(name) for name in quarantined_names),
            "",
        ]
    )
    return "\n".join(lines)


def build_outputs() -> Dict[Path, bytes]:
    chains = build_chains()
    abi_index, names = build_abi_index()
    quarantined_names = sorted(
        _read_json(ABI_LEGACY_ALLOWLIST_PATH)["abis"]
    )
    validate_abi_references(chains, abi_index)
    contract_index, token_index, snapshot_index = build_catalogs(chains, abi_index)
    return {
        CHAINS_OUTPUT: _json_bytes(chains, sort_keys=False),
        ABI_INDEX_OUTPUT: _json_bytes(abi_index),
        CONTRACT_INDEX_OUTPUT: _json_bytes(contract_index),
        TOKEN_INDEX_OUTPUT: _json_bytes(token_index),
        VERIFICATION_SNAPSHOTS_OUTPUT: _json_bytes(snapshot_index),
        ABI_STUB_OUTPUT: _text_bytes(build_abi_stub(names)),
        SUPPORTED_CHAINS_OUTPUT: _text_bytes(build_supported_chains(chains)),
        ABI_PROVENANCE_OUTPUT: _text_bytes(build_abi_provenance(abi_index)),
        CONTRACT_CATALOG_DOC_OUTPUT: _text_bytes(
            build_contract_catalog(contract_index, snapshot_index)
        ),
        TOKEN_CATALOG_DOC_OUTPUT: _text_bytes(build_token_catalog(token_index)),
        THIRD_PARTY_OUTPUT: _text_bytes(
            build_third_party_notices(abi_index, quarantined_names)
        ),
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
