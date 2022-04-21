from typing import Tuple, Optional

import many_abis as ma
import requests
from web3 import Web3
from web3 import exceptions as web3exceptions


def create_dex_router(chain: str, dex_name: str, client: Optional[Tuple[str, Web3]] = None):
    if client is None:
        rpc = ma.get_chain(chain).rpcs.all[0]
        client = Web3(Web3.HTTPProvider(rpc))
    elif isinstance(client, str):
        if client.startswith('http'):
            client = Web3(Web3.HTTPProvider(client))
        elif client.startswith('ws'):
            client = Web3(Web3.WebsocketProvider(client))
        else:
            raise NotImplementedError
    elif not isinstance(client, Web3):
        raise NotImplementedError

    dex = ma.get(chain, dex_name)
    return client.eth.contract(dex.router_address, abi=dex.router_abi)


def get_abi_from_address(address: str, api_key: str, chain_api: str):
    '''
    address: Address want to get abi
    api_key: Explorer API Key
    chain_api: api format for get abi, format like this,
        'https://xxx.xxxscan.xxx/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    '''
    try:
        query = chain_api.format(contract_address=address, api_key=api_key)
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)'
        }
        result = session.get(query, headers=headers)
        session.close()
        result = eval(result.content.decode())
        if result['status'] == '1' and result['message'] == 'OK':
            return result['result']
        else:
            return None
    except Exception as e:
        print(e)
        return None


def get_factory_from_router(router_address: str, api_key: str, chain_api: str, rpc: str) -> Tuple[str, dict]:
    web3 = Web3(Web3.HTTPProvider(rpc))
    router_address = web3.toChecksumAddress(router_address)
    if router_abi := get_abi_from_address(router_address, api_key, chain_api):
        try:
            router_contract = web3.eth.contract(address=router_address, abi=router_abi)
            factory_address = router_contract.functions.factory().call()
            factory_abi = get_abi_from_address(factory_address, api_key, chain_api)
            return factory_address, factory_abi
        except web3exceptions as e:
            print(f"Something wrong with web3, {e}")
        except Exception as e:
            print(e)
