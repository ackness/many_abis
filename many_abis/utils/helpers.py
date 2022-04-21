from ..chains import CHAINS
from ..chains import SUPPORT_CHAIN
from ..chains._base import BaseChain, BaseDEX


def assert_chain_supported(chain: str):
    '''
    chain: UPPER str, like BSC, ETH, ARBITRUM
    '''
    chain_name = chain.upper()
    assert chain_name in SUPPORT_CHAIN, f"{chain} is not supported, support = [{SUPPORT_CHAIN}]"


def get_chain(chain: str) -> BaseChain:
    assert_chain_supported(chain)
    chain_name = chain.upper()
    return CHAINS[chain_name]


def get_support_dex(chain: str) -> list:
    chain_module = get_chain(chain)
    return list(chain_module.dex.keys())


def assert_dex_supported(chain: str, dex: str):
    assert_chain_supported(chain)
    support_dex = get_support_dex(chain)
    assert dex in support_dex, f"{dex} is not supported, support = {support_dex}"


def get_dex(chain: str, dex: str) -> BaseDEX:
    assert_dex_supported(chain, dex)
    dex_name = dex.lower()
    chain_name = chain.upper()
    return CHAINS[chain_name].dex[dex_name]


def get(chain, dex=None):
    # replace "-" to "_"
    chain = chain.replace('-', '_')
    if dex is None:
        return get_chain(chain)
    dex = dex.replace('-', '_')
    return get_dex(chain, dex)


def print_all_dex():
    for name, chain in CHAINS.items():
        print(f"- {name}:")
        for j, (d_name, dex) in enumerate(chain.dex.items()):
            print(f"  - [{j + 1}] [{dex.name}]({dex.website})")
