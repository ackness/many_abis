from .utils import load_chain_swap
from ._base import AttributeDict

CHAIN_SWAP = AttributeDict(load_chain_swap())
SUPPORTED_CHAIN = CHAIN_SWAP.keys()
