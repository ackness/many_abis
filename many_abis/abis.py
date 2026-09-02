from collections.abc import Mapping
from copy import deepcopy
from threading import RLock
from typing import (
    Any,
    Dict as TypingDict,
    Iterable,
    Iterator,
    List,
    NoReturn,
    Optional,
    Self,
    SupportsIndex,
    Tuple,
    Union,
    cast,
)

import requests
from addict import Dict
from eth_utils import is_address, to_checksum_address

from .constants import ETHERSCAN_V2_API, _CHAIN_API_TO_ID
from .meta import ABIMetaData
from .utils import _load_json_resource, load_abi_manifest
from .version import __version__


ABI = List[TypingDict[str, Any]]
_ABI_INDEX = dict(load_abi_manifest()["abis"])
ALL_ABIS_NAME = list(_ABI_INDEX)
_READ_ONLY_ABI_ERROR = "Cached ABI values are read-only; deepcopy before mutating"


def _read_only_abi() -> NoReturn:
    raise TypeError(_READ_ONLY_ABI_ERROR)


class _ReadOnlyABIList(list[Any]):
    """A list-shaped, recursively read-only cached ABI value."""

    def __setitem__(self, key: Any, value: Any) -> None:
        _read_only_abi()

    def __delitem__(self, key: Any) -> None:
        _read_only_abi()

    def __iadd__(self, value: Iterable[Any]) -> Self:  # type: ignore[misc]
        _read_only_abi()

    def __imul__(self, value: SupportsIndex) -> Self:
        _read_only_abi()

    def append(self, value: Any) -> None:
        _read_only_abi()

    def clear(self) -> None:
        _read_only_abi()

    def extend(self, value: Any) -> None:
        _read_only_abi()

    def insert(self, index: SupportsIndex, value: Any) -> None:
        _read_only_abi()

    def pop(self, index: SupportsIndex = -1):
        _read_only_abi()

    def remove(self, value: Any) -> None:
        _read_only_abi()

    def reverse(self) -> None:
        _read_only_abi()

    def sort(self, *args: Any, **kwargs: Any) -> None:
        _read_only_abi()

    def __deepcopy__(self, memo: TypingDict[int, Any]):
        return _thaw_abi_value(self, memo)


class _ReadOnlyABIDict(Dict):
    """An Addict-compatible, recursively read-only cached ABI item."""

    def __init__(self, value: Mapping) -> None:
        dict.__init__(self)
        for key, item in value.items():
            dict.__setitem__(self, key, _freeze_abi_value(item))

    def __setitem__(self, key: Any, value: Any) -> None:
        _read_only_abi()

    def __delitem__(self, key: Any) -> None:
        _read_only_abi()

    def __setattr__(self, name: str, value: Any) -> None:
        _read_only_abi()

    def __delattr__(self, name: str) -> None:
        _read_only_abi()

    def __ior__(self, value: Any):
        _read_only_abi()

    def clear(self) -> None:
        _read_only_abi()

    def pop(self, key: Any, default: Any = None):
        _read_only_abi()

    def popitem(self):
        _read_only_abi()

    def setdefault(self, key: Any, default: Any = None):
        _read_only_abi()

    def update(self, *args: Any, **kwargs: Any) -> None:
        _read_only_abi()

    def __deepcopy__(self, memo: TypingDict[int, Any]):
        return _thaw_abi_value(self, memo)


def _freeze_abi_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return _ReadOnlyABIDict(value)
    if isinstance(value, list):
        return _ReadOnlyABIList(_freeze_abi_value(item) for item in value)
    return value


def _thaw_abi_value(value: Any, memo: TypingDict[int, Any]) -> Any:
    existing = memo.get(id(value))
    if existing is not None:
        return existing
    if isinstance(value, _ReadOnlyABIDict):
        result = Dict()
        memo[id(value)] = result
        for key, item in value.items():
            dict.__setitem__(result, deepcopy(key, memo), deepcopy(item, memo))
        return result
    if isinstance(value, _ReadOnlyABIList):
        result = []
        memo[id(value)] = result
        result.extend(deepcopy(item, memo) for item in value)
        return result
    return deepcopy(value, memo)


def _load_indexed_abi(entry: TypingDict[str, Any]):
    abi = _load_json_resource(entry["resource"])
    if not isinstance(abi, list):
        raise ValueError(
            "ABI resource must contain a JSON array: {}".format(entry["resource"])
        )
    return Dict({"abi": abi}).abi


class _LazyABIRegistry(Mapping):
    """Read-only registry that caches immutable, list-shaped ABI values."""

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

            value = _freeze_abi_value(_load_indexed_abi(entry))
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
    """Return a recursively read-only ABI by its canonical public name."""
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


def _validated_chain_id(value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError("chain_id must be an integer")
    if value <= 0 or value > (1 << 63) - 1:
        raise ValueError("chain_id must be a positive 63-bit integer")
    return value


def _resolve_chain_id(
    chain_api: Optional[Union[str, int]], chain_id: Optional[int]
) -> int:
    if chain_api is not None and chain_id is not None:
        raise ValueError("pass chain_id or chain_api, not both")
    if chain_id is not None:
        return _validated_chain_id(chain_id)
    if isinstance(chain_api, int) and not isinstance(chain_api, bool):
        return _validated_chain_id(chain_api)
    if isinstance(chain_api, str):
        try:
            return _CHAIN_API_TO_ID[chain_api]
        except KeyError as exc:
            raise ValueError(
                "chain_api must be an exact trusted CHAIN_CONTRACT_API constant; "
                "use chain_id for new code"
            ) from exc
    if chain_api is None:
        raise ValueError("chain_id is required")
    raise TypeError("chain_api must be a trusted string selector or integer chain ID")


def get_abi_from_address(
    address: str,
    api_key: str,
    chain_api: Optional[Union[str, int]] = None,
    *,
    chain_id: Optional[int] = None,
) -> Optional[str]:
    """Fetch an ABI from Etherscan V2 without accepting an arbitrary endpoint.

    New code should pass ``chain_id``. The positional ``chain_api`` argument is
    retained only for exact constants exported by ``CHAIN_CONTRACT_API`` and
    for integer chain IDs; arbitrary URL templates are rejected before any
    network request.
    """
    if not isinstance(address, str):
        raise TypeError("address must be a string")
    if not is_address(address) or int(address, 16) == 0:
        raise ValueError("address must be a non-zero 20-byte EVM address")
    if not isinstance(api_key, str):
        raise TypeError("api_key must be a string")
    if not api_key or len(api_key) > 256 or any(ord(char) < 0x20 for char in api_key):
        raise ValueError("api_key must be a non-empty value without control characters")
    resolved_chain_id = _resolve_chain_id(chain_api, chain_id)

    params = {
        "chainid": str(resolved_chain_id),
        "module": "contract",
        "action": "getabi",
        "address": to_checksum_address(address),
        "apikey": api_key,
    }
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; many-abis/{}; "
            "+https://github.com/ackness/many_abis)"
        ).format(__version__)
    }
    try:
        with requests.Session() as session:
            response = session.get(
                ETHERSCAN_V2_API,
                params=params,
                headers=headers,
                timeout=(5, 15),
                allow_redirects=False,
            )
            response.raise_for_status()
            result = response.json()
        if not isinstance(result, dict):
            return None
        if result.get("status") == "1" and result.get("message") == "OK":
            value = result.get("result")
            return value if isinstance(value, str) else None
        return None
    except (requests.RequestException, ValueError):
        return None
