from ._base import AttributeDict
from .arbitrum import ARBITRUM
from .avax import AVAX
from .bsc import BSC
from .bsc_test import BSC_TEST
from .cronos import CRONOS
from .eth import ETH
from .fantom import FANTOM
from .heco import HECO
from .kcc import KCC
from .moonriver import MOONRIVER
from .okex import OKEX
from .polygon import POLYGON


SUPPORT_CHAIN = ['BSC', 'ETH', 'AVAX', 'FANTOM', 'POLYGON', 'CRONOS',
                 'HECO', 'KCC', 'OKEX', 'MOONRIVER', 'ARBITRUM', 'BSC_TEST']
__all__ = ['SUPPORT_CHAIN', 'BSC', 'ETH', 'AVAX', 'FANTOM', 'CRONOS',
           'POLYGON', 'HECO', 'KCC', 'OKEX', 'MOONRIVER', 'BSC_TEST', 'ARBITRUM', 'CHAINS']

CHAINS = AttributeDict(
    **{name: eval(name) for name in SUPPORT_CHAIN}
)
