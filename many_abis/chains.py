from copy import deepcopy
from typing import Any, List, Mapping, NoReturn, Optional, Tuple, Union, cast

from addict import Dict

from .meta import WethMetaData, ChainMetaData, SingleDexMetaData, ChainsMetaData
from .utils import load_chains


_CHAIN_DATA = load_chains()
_SUPPORTED_CHAINS = tuple(_CHAIN_DATA)
_READ_ONLY_CHAIN_ERROR = "Public chain registry snapshots are read-only"


def _read_only_chain() -> NoReturn:
    raise TypeError(_READ_ONLY_CHAIN_ERROR)


def _plain_chain_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _plain_chain_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_plain_chain_value(item) for item in value]
    return deepcopy(value)


class _ReadOnlyChainDict(Dict):
    """An Addict-compatible recursively read-only registry mapping."""

    def __init__(self, value: Mapping) -> None:
        dict.__init__(self)
        for key, item in value.items():
            dict.__setitem__(self, key, _freeze_chain_value(item))

    def __setitem__(self, key: Any, value: Any) -> None:
        _read_only_chain()

    def __delitem__(self, key: Any) -> None:
        _read_only_chain()

    def __setattr__(self, name: str, value: Any) -> None:
        _read_only_chain()

    def __delattr__(self, name: str) -> None:
        _read_only_chain()

    def __ior__(self, value: Any):
        _read_only_chain()

    def clear(self) -> None:
        _read_only_chain()

    def pop(self, key: Any, default: Any = None):
        _read_only_chain()

    def popitem(self):
        _read_only_chain()

    def setdefault(self, key: Any, default: Any = None):
        _read_only_chain()

    def update(self, *args: Any, **kwargs: Any) -> None:
        _read_only_chain()

    def to_dict(self):
        return _plain_chain_value(self)

    def __deepcopy__(self, memo):
        existing = memo.get(id(self))
        if existing is not None:
            return existing
        result = Dict(_plain_chain_value(self))
        memo[id(self)] = result
        return result


def _freeze_chain_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return _ReadOnlyChainDict(value)
    if isinstance(value, list):
        return tuple(_freeze_chain_value(item) for item in value)
    return value


CHAINS: ChainsMetaData = cast(ChainsMetaData, _ReadOnlyChainDict(_CHAIN_DATA))
SUPPORTED_CHAINS: Tuple[str, ...] = _SUPPORTED_CHAINS


def _public_copy(value: Any) -> Any:
    if isinstance(value, Mapping):
        return Dict(deepcopy(value))
    return deepcopy(value)


def all_chains() -> List[str]:
    return list(_SUPPORTED_CHAINS)


def get_chain_by_name(name: str) -> ChainMetaData:
    if name not in _CHAIN_DATA:
        raise ValueError(f"Chain {name} not supported")
    return cast(ChainMetaData, _public_copy(_CHAIN_DATA[name]))


def get_chain_by_id(chain_id: int) -> ChainMetaData:
    for name, info in _CHAIN_DATA.items():
        if "chain_id" not in info:
            raise ValueError(f"Chain {name} does not have chain_id")
        if info["chain_id"] == chain_id:
            return cast(ChainMetaData, _public_copy(info))
    raise ValueError(f"Chain id {chain_id} not supported")


def get_chain(
    name: Optional[str] = None,
    chain_id: Optional[int] = None,
) -> ChainMetaData:
    if name is None and chain_id is None:
        raise ValueError("Must provide either name or chain_id")
    if name is not None:
        name = name.lower()
        return get_chain_by_name(name)
    if chain_id is None:  # Defensive narrowing for type checkers.
        raise ValueError("Must provide either name or chain_id")
    return get_chain_by_id(int(chain_id))


def chain(*args, **kwargs) -> ChainMetaData:
    return get_chain(*args, **kwargs)


def get(*keys) -> Union[ChainMetaData, SingleDexMetaData, WethMetaData, ChainsMetaData]:
    value: Any = _CHAIN_DATA
    try:
        for key in keys:
            value = value[key]
        return cast(
            Union[ChainMetaData, SingleDexMetaData, WethMetaData, ChainsMetaData],
            _public_copy(value),
        )
    except KeyError as e:
        raise KeyError(f"{keys} is not exist") from e
