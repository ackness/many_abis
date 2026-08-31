from collections.abc import Mapping
from copy import deepcopy
from threading import RLock
from typing import Any, Dict as TypingDict, Iterator, List, Optional, Tuple, cast

import requests
from addict import Dict

from .meta import ABIMetaData
from .utils import _load_json_resource, load_abi_manifest


ABI = List[TypingDict[str, Any]]
_ABI_INDEX = dict(load_abi_manifest()["abis"])
ALL_ABIS_NAME = list(_ABI_INDEX)


def _load_indexed_abi(entry: TypingDict[str, Any]):
    abi = _load_json_resource(entry["resource"])
    if not isinstance(abi, list):
        raise ValueError(
            "ABI resource must contain a JSON array: {}".format(entry["resource"])
        )
    return Dict({"abi": abi}).abi


class _LazyABIRegistry(Mapping):
    """Read-only registry that parses each ABI at most once, on demand."""

    __slots__ = ("_cache", "_index", "_lock")

    def __init__(self, index: TypingDict[str, TypingDict[str, Any]]) -> None:
        object.__setattr__(self, "_index", dict(index))
        object.__setattr__(self, "_cache", {})
        object.__setattr__(self, "_lock", RLock())

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("ABI registry is read-only")

    def __getitem__(self, name: str):
        try:
            entry = self._index[name]
        except KeyError as exc:
            raise KeyError("ABI {} is not supported".format(name)) from exc

        with self._lock:
            if name in self._cache:
                return self._cache[name]

            value = _load_indexed_abi(entry)
            self._cache[name] = value
            return value

    def __iter__(self) -> Iterator[str]:
        return iter(self._index)

    def __len__(self) -> int:
        return len(self._index)

    def __contains__(self, name: object) -> bool:
        return name in self._index

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __dir__(self) -> List[str]:
        return sorted(set(super().__dir__()) | set(self._index))

    def __repr__(self) -> str:
        return "<LazyABIRegistry loaded={} total={}>".format(
            len(self._cache), len(self._index)
        )

    def clear_cache(self) -> None:
        with self._lock:
            self._cache.clear()

    def loaded_names(self) -> List[str]:
        with self._lock:
            return sorted(self._cache)

    def to_dict(self) -> TypingDict[str, ABI]:
        """Return eager recursively plain data, matching ``addict.Dict``."""
        return Dict({name: self[name] for name in self}).to_dict()

    def copy(self) -> Dict:
        """Return an eager shallow Addict copy, matching legacy behavior."""
        value = Dict()
        for name in self:
            dict.__setitem__(value, name, self[name])
        return value


ABIS = cast(ABIMetaData, _LazyABIRegistry(_ABI_INDEX))


def get_abi(name: str):
    """Return a cached ABI by its canonical public name."""
    if not isinstance(name, str):
        raise TypeError("ABI name must be a string")
    return cast(_LazyABIRegistry, ABIS)[name.upper()]


def get_abi_info(name: str) -> TypingDict[str, Any]:
    """Return a defensive copy of provenance and identity metadata for one ABI."""
    if not isinstance(name, str):
        raise TypeError("ABI name must be a string")
    canonical_name = name.upper()
    try:
        return cast(TypingDict[str, Any], deepcopy(_ABI_INDEX[canonical_name]))
    except KeyError as exc:
        raise KeyError("ABI {} is not supported".format(canonical_name)) from exc


def find_abis(
    contract_role: Optional[str] = None,
    interface_name: Optional[str] = None,
    provenance_status: Optional[str] = None,
) -> List[str]:
    """List ABI names matching optional manifest metadata filters."""
    role_filter = contract_role.lower() if contract_role is not None else None
    status_filter = (
        provenance_status.lower() if provenance_status is not None else None
    )
    matches = []
    for name, entry in _ABI_INDEX.items():
        if role_filter is not None and entry["contract_role"].lower() != role_filter:
            continue
        if interface_name is not None and entry["interface_name"] != interface_name:
            continue
        if (
            status_filter is not None
            and entry["provenance"]["status"].lower() != status_filter
        ):
            continue
        matches.append(name)
    return matches


def clear_abi_cache() -> None:
    cast(_LazyABIRegistry, ABIS).clear_cache()


def loaded_abis() -> List[str]:
    """Return names loaded so far without loading additional ABI files."""
    return cast(_LazyABIRegistry, ABIS).loaded_names()


def all_abis() -> Tuple[List[str], ABIMetaData]:
    """Eagerly load a fresh registry, preserving the legacy helper contract."""
    values = {
        name: _load_indexed_abi(entry) for name, entry in _ABI_INDEX.items()
    }
    return list(_ABI_INDEX), cast(ABIMetaData, Dict(values))


def get_abi_from_address(
    address: str,
    api_key: str,
    chain_api: str,
) -> Optional[str]:
    """Fetch a verified ABI string from an Etherscan-compatible API."""
    try:
        query = chain_api.format(contract_address=address, api_key=api_key)
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (compatible; many-abis/0.3; "
                "+https://github.com/ackness/many_abis)"
            )
        }
        with requests.Session() as session:
            response = session.get(query, headers=headers, timeout=15)
            response.raise_for_status()
            result = response.json()
        if not isinstance(result, dict):
            return None
        if result.get("status") == "1" and result.get("message") == "OK":
            value = result.get("result")
            return value if isinstance(value, str) else None
        return None
    except (requests.RequestException, ValueError, KeyError, IndexError):
        return None
