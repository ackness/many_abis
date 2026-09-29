#!/usr/bin/env python3
"""Refresh explicit on-chain verification snapshots using registry RPCs."""

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple
from urllib.parse import urlsplit

import requests
from eth_utils import keccak, to_checksum_address


ROOT = Path(__file__).resolve().parents[1]
CHAIN_SOURCE_DIR = ROOT / "registry" / "chains"
CHAIN_ORDER_PATH = ROOT / "registry" / "chain-order.json"
SNAPSHOT_PATH = ROOT / "registry" / "verification-snapshots.json"

IMPLEMENTATION_SLOT = (
    "0x360894a13ba1a3210667c828492db98dca3e2076"
    "cc3735a920a3ca505d382bbc"
)
ADMIN_SLOT = (
    "0xb53127684a568b3173ae13b9f8a6016e243e"
    "63b6e8ee1178d6a717850b5d6103"
)
BEACON_SLOT = (
    "0xa3f0ad74e5423aebfd80d3ef4346578335a9"
    "a72aeaee59ff6cb3582b35133d50"
)
DECIMALS_SELECTOR = "0x313ce567"
SYMBOL_SELECTOR = "0x95d89b41"


class VerificationError(RuntimeError):
    pass


def _rpc_log_label(rpc_url: str) -> str:
    """Return a credential-free RPC label suitable for CI output."""
    parsed = urlsplit(rpc_url)
    hostname = parsed.hostname or "invalid-rpc"
    try:
        port = parsed.port
    except ValueError:
        port = None
    if port is not None:
        hostname = "{}:{}".format(hostname, port)
    return "{}://{}".format(parsed.scheme or "https", hostname)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    content = (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
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


def _load_chains() -> Dict[str, Any]:
    if __package__:
        from .generate_registry import _load_deployments
    else:
        from generate_registry import _load_deployments

    order = _read_json(CHAIN_ORDER_PATH)["chains"]
    chains = {
        slug: _read_json(CHAIN_SOURCE_DIR / (slug + ".json"))["data"]
        for slug in order
    }
    for deployment in _load_deployments(chains):
        chains[deployment["chain"]].setdefault("deployments", []).append(deployment)
    return chains


def _chain_targets(chain: Mapping[str, Any]) -> Dict[str, Tuple[str, bool]]:
    """Return lowercase-keyed addresses with deterministic token-role merging."""
    targets = {}  # type: Dict[str, Tuple[str, bool]]

    def add(address: str, is_token: bool) -> None:
        key = address.lower()
        current = targets.get(key)
        checksum_address = to_checksum_address(address)
        targets[key] = (
            checksum_address,
            is_token or (current[1] if current is not None else False),
        )

    add(chain["weth"]["address"], True)
    for field in ("stable_coins", "test_coins"):
        for address in chain.get(field, {}).values():
            add(address, True)
    for dex in chain["dex"].values():
        add(dex["factory_address"], False)
        add(dex["router_address"], False)
    for deployment in chain.get("deployments", []):
        add(deployment["address"], False)
    return targets


def _rpc_request(
    session: requests.Session, url: str, payload: Any, timeout: float
) -> Any:
    response = session.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    try:
        return response.json()
    except ValueError as exc:
        raise VerificationError("{} returned non-JSON RPC data".format(url)) from exc


def _rpc_call(
    session: requests.Session,
    url: str,
    method: str,
    params: Sequence[Any],
    timeout: float,
) -> Any:
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    data = _rpc_request(session, url, payload, timeout)
    if not isinstance(data, dict) or "result" not in data:
        error = data.get("error") if isinstance(data, dict) else data
        raise VerificationError(
            "{} {} failed: {}".format(url, method, error)
        )
    return data["result"]


def _rpc_many(
    session: requests.Session,
    url: str,
    calls: Sequence[Tuple[str, str, Sequence[Any]]],
    timeout: float,
) -> Dict[str, Any]:
    payload = [
        {"jsonrpc": "2.0", "id": index, "method": method, "params": params}
        for index, (_, method, params) in enumerate(calls, start=1)
    ]
    try:
        data = _rpc_request(session, url, payload, timeout)
        if not isinstance(data, list):
            raise VerificationError("batch RPC response is not a list")
        by_id = {item.get("id"): item for item in data if isinstance(item, dict)}
        results = {}
        for index, (label, method, _) in enumerate(calls, start=1):
            item = by_id.get(index)
            if item is None or "result" not in item:
                error = item.get("error") if isinstance(item, dict) else item
                raise VerificationError(
                    "{} {} failed: {}".format(url, method, error)
                )
            results[label] = item["result"]
        return results
    except (requests.RequestException, VerificationError, ValueError):
        return {
            label: _rpc_call(session, url, method, params, timeout)
            for label, method, params in calls
        }


def _decode_word(value: str, label: str) -> bytes:
    if (
        not isinstance(value, str)
        or not value.startswith("0x")
        or len(value) != 66
    ):
        raise VerificationError("{} must be one 32-byte ABI word".format(label))
    try:
        return bytes.fromhex(value[2:])
    except ValueError as exc:
        raise VerificationError("{} returned malformed hex data".format(label)) from exc


def _storage_address(value: str) -> Optional[str]:
    raw = _decode_word(value, "EIP-1967 storage")
    if any(raw[:12]):
        raise VerificationError("EIP-1967 address has non-zero high bytes")
    if not any(raw[12:]):
        return None
    return to_checksum_address("0x" + raw[12:].hex())


def _decode_uint8(value: str, label: str) -> int:
    number = int.from_bytes(_decode_word(value, label), "big")
    if number > 255:
        raise VerificationError("{} is outside uint8".format(label))
    return number


def _code_hash(code: str) -> str:
    if not isinstance(code, str) or not code.startswith("0x") or code == "0x":
        raise VerificationError("registered address has no runtime bytecode")
    try:
        raw = bytes.fromhex(code[2:])
    except ValueError as exc:
        raise VerificationError("RPC returned malformed runtime bytecode") from exc
    return "0x" + keccak(raw).hex()


def _decode_symbol(value: str) -> str:
    if not isinstance(value, str) or not value.startswith("0x"):
        raise VerificationError("symbol() returned malformed data")
    try:
        raw = bytes.fromhex(value[2:])
    except ValueError as exc:
        raise VerificationError("symbol() returned malformed hex data") from exc
    if len(raw) >= 32 and int.from_bytes(raw[:32], "big") == 32:
        if len(raw) < 64:
            raise VerificationError("symbol() returned truncated dynamic data")
        length = int.from_bytes(raw[32:64], "big")
        padded_length = ((length + 31) // 32) * 32
        if len(raw) != 64 + padded_length:
            raise VerificationError("symbol() returned invalid dynamic length")
        payload = raw[64 : 64 + length]
        if any(raw[64 + length :]):
            raise VerificationError("symbol() returned non-zero ABI padding")
    elif len(raw) == 32:
        payload = raw[:32].rstrip(b"\x00")
    else:
        raise VerificationError("symbol() must return string or bytes32 data")
    try:
        symbol = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise VerificationError("symbol() returned invalid UTF-8") from exc
    if not symbol.strip() or "\x00" in symbol or len(symbol) > 64:
        raise VerificationError("symbol() returned an unusable value")
    return symbol


def _normalized_block_hash(value: Any) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 66
        or not value.startswith("0x")
    ):
        raise VerificationError("RPC returned a malformed block hash")
    try:
        bytes.fromhex(value[2:])
    except ValueError as exc:
        raise VerificationError("RPC returned a malformed block hash") from exc
    return value.lower()


def _confirm_block(
    session: requests.Session,
    url: str,
    block_parameter: str,
    expected_number: int,
    expected_hash: str,
    timeout: float,
) -> None:
    confirmed = _rpc_call(
        session,
        url,
        "eth_getBlockByNumber",
        [block_parameter, False],
        timeout,
    )
    if not isinstance(confirmed, dict):
        raise VerificationError("pinned block disappeared during refresh")
    try:
        confirmed_number = int(confirmed["number"], 16)
        confirmed_hash = _normalized_block_hash(confirmed["hash"])
    except (KeyError, TypeError, ValueError) as exc:
        raise VerificationError("RPC returned malformed pinned block data") from exc
    if confirmed_number != expected_number or confirmed_hash != expected_hash:
        raise VerificationError("pinned block changed during refresh; retry")


def _collect_chain(
    slug: str,
    chain: Mapping[str, Any],
    block_tag: str,
    timeout: float,
    addresses: Optional[Sequence[str]] = None,
) -> Tuple[Dict[str, Any], str, int]:
    targets = _chain_targets(chain)
    if addresses is not None:
        selected = {address.lower() for address in addresses}
        if not selected or not selected.issubset(targets):
            raise VerificationError("addresses must select registered chain targets")
        targets = {key: value for key, value in targets.items() if key in selected}
    errors = []
    for rpc_url in chain["rpc"]:
        try:
            with requests.Session() as session:
                actual_chain_id = int(
                    _rpc_call(session, rpc_url, "eth_chainId", [], timeout), 16
                )
                if actual_chain_id != chain["chain_id"]:
                    raise VerificationError(
                        "expected chain {}, received {}".format(
                            chain["chain_id"], actual_chain_id
                        )
                    )
                block = _rpc_call(
                    session,
                    rpc_url,
                    "eth_getBlockByNumber",
                    [block_tag, False],
                    timeout,
                )
                if not isinstance(block, dict) or not block.get("hash"):
                    raise VerificationError("{} block is unavailable".format(block_tag))
                block_hash = _normalized_block_hash(block["hash"])
                block_number = int(block["number"], 16)
                block_parameter = block["number"]

                calls = []
                for prefix in sorted(targets):
                    address, is_token = targets[prefix]
                    calls.extend(
                        [
                            (
                                prefix + ":code",
                                "eth_getCode",
                                [address, block_parameter],
                            ),
                            (
                                prefix + ":implementation",
                                "eth_getStorageAt",
                                [address, IMPLEMENTATION_SLOT, block_parameter],
                            ),
                            (
                                prefix + ":admin",
                                "eth_getStorageAt",
                                [address, ADMIN_SLOT, block_parameter],
                            ),
                            (
                                prefix + ":beacon",
                                "eth_getStorageAt",
                                [address, BEACON_SLOT, block_parameter],
                            ),
                        ]
                    )
                    if is_token:
                        calls.extend(
                            [
                                (
                                    prefix + ":decimals",
                                    "eth_call",
                                    [
                                        {"to": address, "data": DECIMALS_SELECTOR},
                                        block_parameter,
                                    ],
                                ),
                                (
                                    prefix + ":symbol",
                                    "eth_call",
                                    [
                                        {"to": address, "data": SYMBOL_SELECTOR},
                                        block_parameter,
                                    ],
                                ),
                            ]
                        )
                values = _rpc_many(session, rpc_url, calls, timeout)

                implementations = {}
                for prefix in targets:
                    implementation = _storage_address(
                        values[prefix + ":implementation"]
                    )
                    if implementation is not None:
                        implementations[prefix] = implementation
                implementation_values = (
                    _rpc_many(
                        session,
                        rpc_url,
                        [
                            (
                                prefix,
                                "eth_getCode",
                                [implementation, block_parameter],
                            )
                            for prefix, implementation in sorted(
                                implementations.items()
                            )
                        ],
                        timeout,
                    )
                    if implementations
                    else {}
                )

                _confirm_block(
                    session,
                    rpc_url,
                    block_parameter,
                    block_number,
                    block_hash,
                    timeout,
                )

                observed_at = datetime.now(timezone.utc).isoformat().replace(
                    "+00:00", "Z"
                )
                snapshots = {}
                for prefix in sorted(targets):
                    address, is_token = targets[prefix]
                    code = values[prefix + ":code"]
                    implementation = implementations.get(prefix)
                    token_metadata = None
                    if is_token:
                        decimals = _decode_uint8(
                            values[prefix + ":decimals"], "decimals()"
                        )
                        token_metadata = {
                            "decimals": decimals,
                            "symbol": _decode_symbol(values[prefix + ":symbol"]),
                        }
                    implementation_hash = None
                    if implementation is not None:
                        implementation_hash = _code_hash(
                            implementation_values[prefix]
                        )
                    verification_id = "{}:{}".format(slug, prefix)
                    snapshots[verification_id] = {
                        "address": address,
                        "block_hash": block_hash,
                        "block_number": block_number,
                        "block_tag": block_tag,
                        "chain": slug,
                        "chain_id": chain["chain_id"],
                        "code_size": (len(code) - 2) // 2,
                        "eip1967": {
                            "admin": _storage_address(values[prefix + ":admin"]),
                            "beacon": _storage_address(values[prefix + ":beacon"]),
                            "implementation": implementation,
                            "implementation_code_keccak256": implementation_hash,
                        },
                        "observed_at": observed_at,
                        "rpc_url": rpc_url,
                        "runtime_code_keccak256": _code_hash(code),
                        "token_metadata": token_metadata,
                    }
                return snapshots, rpc_url, block_number
        except (requests.RequestException, VerificationError, ValueError) as exc:
            errors.append(
                "{}: {}".format(_rpc_log_label(rpc_url), type(exc).__name__)
            )
    raise VerificationError("{} failed: {}".format(slug, "; ".join(errors)))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--chain",
        action="append",
        dest="chains",
        help="refresh one chain slug; repeat for multiple chains",
    )
    parser.add_argument(
        "--block-tag",
        choices=("latest", "safe", "finalized"),
        default="latest",
    )
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument(
        "--missing-only", action="store_true",
        help="collect new addresses while preserving existing pinned snapshots",
    )
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args(argv)

    chains = _load_chains()
    selected = arguments.chains or list(chains)
    unknown = sorted(set(selected) - set(chains))
    if unknown:
        parser.error("unknown chains: {}".format(", ".join(unknown)))

    document = _read_json(SNAPSHOT_PATH)
    retained = {
        key: value
        for key, value in document.get("snapshots", {}).items()
        if arguments.missing_only or value.get("chain") not in selected
    }
    for slug in selected:
        addresses = None
        if arguments.missing_only:
            addresses = [
                address for address in _chain_targets(chains[slug])
                if "{}:{}".format(slug, address) not in retained
            ]
            if not addresses:
                continue
        snapshots, rpc_url, block_number = _collect_chain(
            slug, chains[slug], arguments.block_tag, arguments.timeout, addresses
        )
        retained.update(snapshots)
        print(
            "{}: {} addresses at block {} via {}".format(
                slug, len(snapshots), block_number, _rpc_log_label(rpc_url)
            )
        )

    output = {
        "$schema": "schemas/verification-snapshots.schema.json",
        "schema_version": 1,
        "snapshots": retained,
    }
    if arguments.write:
        _write_json(SNAPSHOT_PATH, output)
        print("wrote {} snapshots".format(len(retained)))
    else:
        print("dry run complete; pass --write to update the registry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
