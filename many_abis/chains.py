from typing import Any, List, Optional, Union

from addict import Dict

from .meta import WethMetaData, ChainMetaData, SingleDexMetaData, ChainsMetaData
from .utils import load_chains

CHAINS: ChainsMetaData = Dict(load_chains())
SUPPORTED_CHAINS: List[str] = list(CHAINS.keys())


def all_chains() -> List[str]:
    return list(SUPPORTED_CHAINS)


def get_chain_by_name(name: str) -> ChainMetaData:
    if name not in CHAINS:
        raise ValueError(f"Chain {name} not supported")
    return CHAINS[name]


def get_chain_by_id(chain_id: int) -> ChainMetaData:
    for name, info in CHAINS.items():
        if "chain_id" not in info:
            raise ValueError(f"Chain {name} does not have chain_id")
        if info["chain_id"] == chain_id:
            return CHAINS[name]
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
    value: Any = CHAINS
    try:
        for key in keys:
            value = value[key]
        return value
    except KeyError as e:
        raise KeyError(f"{keys} is not exist") from e
