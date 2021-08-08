import requests
import importlib
from web3 import Web3
from web3 import exceptions as web3exceptions
from typing import Tuple, Optional

from .contract_api_enum import CHAIN_CONTRACT_API as contract_api
from .chain_rpc_enum import CHAIN_RPC_API as rpc
from ..assets import SUPPORT_CHAIN


def get_abi_from_address(address: str, api_key: str, chain_api: str=contract_api.BSC) -> Optional[dict]:
    query = chain_api.format(contract_address=address, api_key=api_key)
    session = requests.Session()
    headers = {'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)'}
    result = session.get(query, headers=headers)
    session.close()
    result = eval(result.content.decode())

    if result['status'] == '1' and result['message'] == 'OK':
        return result['result']
    else:
        return None

def get_factory_from_router(router_address: str, api_key: str, chain_api: str=contract_api.BSC, rpc: str=rpc.BSC) -> Tuple[str, dict]:
    web3 = Web3(Web3.HTTPProvider(rpc))
    router_address = web3.toChecksumAddress(router_address)
    router_abi = get_abi_from_address(router_address, api_key, chain_api)
    if router_abi:
        try:
            router_contract = web3.eth.contract(address=router_address, abi=router_abi)
            factory_address = router_contract.functions.factory().call()
            factory_abi = get_abi_from_address(factory_address, api_key, chain_api)
            return factory_address, factory_abi
        except web3exceptions.ABIFunctionNotFound:
            # some contract use different factory name, for example 0xbf6527834dbb89cdc97a79fcd62e6c08b19f8ec0
            router_contract = web3.eth.contract(address=router_address, abi=router_abi)
            factory_address = router_contract.functions.FACTORY().call()
            factory_abi = get_abi_from_address(factory_address, api_key, chain_api)
            return factory_address, factory_abi
        except Exception as e:
            print(e)

def assert_chain_supported(chain: str):
    assert chain in SUPPORT_CHAIN, f"{chain} is not supported, support = [{SUPPORT_CHAIN}]" 

def assert_dex_supported(chain: str, dex: str):
    assert_chain_supported(chain)
    support_dex = get_support_dex(chain)
    assert dex in support_dex, f"{dex} is not supported, support = {support_dex}"

def get_chain(chain: str='BSC') -> dict:
    return get_chain_info(chain)

def get_support_chain() -> list:
    return SUPPORT_CHAIN

def get_chain_module(chain: str='BSC'):
    chain = chain.upper()
    assert_chain_supported(chain)
    chain_module = importlib.import_module(f".assets.{chain}", package='many_abis')
    return chain_module

def get_chain_rpc(chain: str='BSC') -> list:
    chain_module = get_chain_module(chain)
    return chain_module.RPC

def get_chain_charts(chain: str='BSC') -> dict:
    chain_module = get_chain_module(chain)
    return chain_module.CHARTS

def get_chain_info(chain: str='BSC') -> dict:
    chain_module = get_chain_module(chain)
    return chain_module.BASIC

def get_chain_weth(chain: str='BSC') -> dict:
    chain_module = get_chain_module(chain)
    return chain_module.BASIC['weth']

def get_chain_stable_coins(chain: str='BSC') -> dict:
    chain_module = get_chain_module(chain)
    return chain_module.BASIC['coins']

def get_chain_explorer(chain: str='BSC') -> str:
    chain_module = get_chain_module(chain)
    return chain_module.BASIC['explorer']

def get_support_dex(chain: str='BSC') -> list:
    chain_module = get_chain_module(chain)
    return chain_module.SUPPORT_DEX

def get_dex_module(chain: str='BSC', dex: str='pancake_v2'):
    assert_dex_supported(chain, dex)
    dex_module = importlib.import_module(f".assets.{chain}.{dex}", package='many_abis')
    return dex_module

def get_dex(chain: str='BSC', dex: str='pancake_v2') -> dict:
    dex_module = get_dex_module(chain, dex)
    return dex_module.DEX

def get_module(chain: str, dex: str):
    return get_chain_module(chain), get_dex_module(chain, dex)

def get(chain: str, dex: str) -> Tuple[dict, dict]:
    basic = get_chain_info(chain)
    dex = get_dex(chain, dex)
    return basic, dex

def print_all_support():
    for i, chain in enumerate(SUPPORT_CHAIN):
        print(f"- {chain}:")
        supported_dex = get_support_dex(chain)
        print('  - DEX:')
        for j, dex in enumerate(supported_dex):
            dex_info = get_dex(chain, dex)
            print(f"    - [{j}] [{dex_info['name']}]({dex_info['website']})")


