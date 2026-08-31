"""Read-only access to generated contract, token, and verification catalogs."""

from copy import deepcopy
from threading import RLock
from typing import Any, Dict, List, Optional, Union, cast

from eth_utils import is_address

from .utils import (
    load_contract_manifest,
    load_token_manifest,
    load_verification_manifest,
)


__all__ = [
    "all_contract_ids",
    "all_token_ids",
    "get_contract",
    "get_token",
    "get_verification",
    "list_contracts",
    "list_tokens",
]


_CATALOG_LOCK = RLock()
_CONTRACTS = None  # type: Optional[Dict[str, Dict[str, Any]]]
_TOKENS = None  # type: Optional[Dict[str, Dict[str, Any]]]
_VERIFICATIONS = None  # type: Optional[Dict[str, Dict[str, Any]]]


def _contracts() -> Dict[str, Dict[str, Any]]:
    global _CONTRACTS
    with _CATALOG_LOCK:
        if _CONTRACTS is None:
            _CONTRACTS = cast(
                Dict[str, Dict[str, Any]],
                load_contract_manifest()["contracts"],
            )
        return _CONTRACTS


def _tokens() -> Dict[str, Dict[str, Any]]:
    global _TOKENS
    with _CATALOG_LOCK:
        if _TOKENS is None:
            _TOKENS = cast(
                Dict[str, Dict[str, Any]], load_token_manifest()["tokens"]
            )
        return _TOKENS


def _verifications() -> Dict[str, Dict[str, Any]]:
    global _VERIFICATIONS
    with _CATALOG_LOCK:
        if _VERIFICATIONS is None:
            _VERIFICATIONS = cast(
                Dict[str, Dict[str, Any]],
                load_verification_manifest()["snapshots"],
            )
        return _VERIFICATIONS


def all_contract_ids() -> List[str]:
    return list(_contracts())


def all_token_ids() -> List[str]:
    return list(_tokens())


def get_contract(contract_id: str) -> Dict[str, Any]:
    """Return a defensive copy of one logical contract record."""
    if not isinstance(contract_id, str):
        raise TypeError("contract_id must be a string")
    normalized = contract_id.lower()
    try:
        return cast(Dict[str, Any], deepcopy(_contracts()[normalized]))
    except KeyError as exc:
        raise KeyError("Contract {} is not registered".format(contract_id)) from exc


def list_contracts(
    chain: Optional[str] = None,
    role: Optional[str] = None,
    protocol: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return defensive copies of contract records matching optional filters."""
    chain_filter = chain.lower() if chain is not None else None
    role_filter = role.lower() if role is not None else None
    protocol_filter = protocol.lower() if protocol is not None else None
    result = []
    for record in _contracts().values():
        if chain_filter is not None and record["chain"].lower() != chain_filter:
            continue
        if role_filter is not None and record["role"].lower() != role_filter:
            continue
        record_protocol = record["protocol"]
        if (
            protocol_filter is not None
            and (record_protocol is None or record_protocol.lower() != protocol_filter)
        ):
            continue
        result.append(cast(Dict[str, Any], deepcopy(record)))
    return result


def get_token(chain: str, symbol: str) -> Dict[str, Any]:
    """Return one configured token by chain slug and case-insensitive symbol."""
    if not isinstance(chain, str) or not isinstance(symbol, str):
        raise TypeError("chain and symbol must be strings")
    expected_chain = chain.lower()
    expected_symbol = symbol.casefold()
    for record in _tokens().values():
        if (
            record["chain"].lower() == expected_chain
            and record["configured_symbol"].casefold() == expected_symbol
        ):
            return cast(Dict[str, Any], deepcopy(record))
    raise KeyError("Token {}:{} is not registered".format(chain, symbol))


def list_tokens(
    chain: Optional[str] = None,
    role: Optional[str] = None,
    origin: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return defensive copies of token records matching optional filters."""
    chain_filter = chain.lower() if chain is not None else None
    role_filter = role.lower() if role is not None else None
    origin_filter = origin.lower() if origin is not None else None
    result = []
    for record in _tokens().values():
        if chain_filter is not None and record["chain"].lower() != chain_filter:
            continue
        if role_filter is not None and record["role"].lower() != role_filter:
            continue
        if origin_filter is not None and record["origin"].lower() != origin_filter:
            continue
        result.append(cast(Dict[str, Any], deepcopy(record)))
    return result


def get_verification(
    chain: Union[str, int], address: str
) -> Dict[str, Any]:
    """Return the pinned on-chain snapshot for a chain and address."""
    if not isinstance(chain, (str, int)) or isinstance(chain, bool):
        raise TypeError("chain must be a slug or chain ID")
    if not isinstance(address, str) or not is_address(address):
        raise ValueError("address must be a 20-byte EVM address")

    normalized_address = address.lower()
    if isinstance(chain, str):
        key = "{}:{}".format(chain.lower(), normalized_address)
        try:
            return cast(Dict[str, Any], deepcopy(_verifications()[key]))
        except KeyError as exc:
            raise KeyError(
                "No verification for {}:{}".format(chain, address)
            ) from exc

    for record in _verifications().values():
        if (
            record["chain_id"] == chain
            and record["address"].lower() == normalized_address
        ):
            return cast(Dict[str, Any], deepcopy(record))
    raise KeyError("No verification for {}:{}".format(chain, address))
