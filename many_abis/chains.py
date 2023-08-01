from functools import reduce
from typing import Union

from addict import Dict

from .meta import WethMetaData, ChainMetaData, SingleDexMetaData, ChainsMetaData
from .utils import load_chains

CHAINS: ChainsMetaData = Dict(load_chains())
SUPPORTED_CHAINS: list[str] = list(CHAINS.keys())


def all_chains() -> list[str]:
    return SUPPORTED_CHAINS


def get_chain_by_name(name: str) -> ChainMetaData:
    assert name in SUPPORTED_CHAINS, f"Chain {name} not supported"
    return CHAINS[name]


def get_chain_by_id(chain_id: int) -> ChainMetaData:
    for name, info in CHAINS.items():
        if "chain_id" not in info:
            raise ValueError(f"Chain {name} does not have chain_id")
        if info["chain_id"] == chain_id:
            return CHAINS[name]
    raise ValueError(f"Chain id {chain_id} not supported")


def get_chain(name=None, chain_id=None) -> ChainMetaData:
    assert name or chain_id, "Must provide either name or chain_id"
    if name:
        name = name.lower()
        return get_chain_by_name(name)
    elif chain_id:
        chain_id = int(chain_id)
        return get_chain_by_id(chain_id)


def chain(*args, **kwargs) -> ChainMetaData:
    return get_chain(*args, **kwargs)


def get(*keys) -> Union[ChainMetaData, SingleDexMetaData, WethMetaData, ChainsMetaData]:
    try:
        return reduce(lambda d, key: d[key], keys, CHAINS)
    except KeyError as e:
        raise KeyError(f"{keys} is not exist") from e
