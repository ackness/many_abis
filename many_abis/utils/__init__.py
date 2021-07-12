import requests
import importlib
from web3 import Web3
from web3 import exceptions as web3exceptions

from .contract_api_enum import CHAIN_CONTRACT_API as contract_api
from .chain_rpc_enum import CHAIN_RPC_API as rpc
from ..assets import SUPPORT_CHAIN


def get_abi_from_address(address, api_key, chain_api=contract_api.BSC):
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


def get_factory_from_router(router_address, api_key, chain_api=contract_api.BSC, rpc=rpc.BSC):
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


def get_chain():
    return SUPPORT_CHAIN


def get_dex(chain='BSC'):
    chain_module = importlib.import_module(f".assets.{chain}", package='many_abis')
    return chain_module.SUPPORT_DEX


def get(chain, dex):
    assert chain in SUPPORT_CHAIN, f"{chain} is not supported, support = [{SUPPORT_CHAIN}]"
    chain_module = importlib.import_module(f".assets.{chain}", package='many_abis')
    assert dex in chain_module.SUPPORT_DEX, f"{dex} is not supported, support = [{chain_module.SUPPORT_DEX}]"
    dex_module = importlib.import_module(f".assets.{chain}.{dex}", package='many_abis')
    dex = dex_module.DEX
    weth = chain_module.WETH
    return dex, weth


def print_all_support():
    for i, chain in enumerate(SUPPORT_CHAIN):
        print(f"- {chain}:")
        chain_module = importlib.import_module(f".assets.{chain}", package='many_abis')
        print('  - DEX:')
        for j, dex in enumerate(chain_module.SUPPORT_DEX):
            dex_module = importlib.import_module(f".assets.{chain}.{dex}", package='many_abis')
            print(f"    - [{j}] [{dex_module.DEX['name']}]({dex_module.DEX['website']})")


