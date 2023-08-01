from pathlib import PurePath

import requests
from addict import Dict

from .meta import ABIMetaData
from .utils import load_all_abis


# __all__ = ["ABIS"]

def all_abis() -> tuple[list[str], ABIMetaData]:
    all_abis = load_all_abis()
    names = []
    all_abis_rename = {}
    for k, v in all_abis.items():
        ns = list(PurePath(k).parts)[2:]
        # ns = k.split('/')[2:]  # only for linux or mac
        name = '_'.join(ns).upper()
        names.append(name)
        all_abis_rename[name] = v
    return names, Dict(all_abis_rename)


ALL_ABIS_NAME, ABIS = all_abis()


def get_abi_from_address(address: str, api_key: str, chain_api: str):
    '''
    address: Address want to get abi
    api_key: Explorer API Key
    chain_api: api format for get abi, format like this,
        'https://xxx.xxxscan.xxx/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    '''
    try:
        query = chain_api.format(contract_address=address, api_key=api_key)
        # print(query)
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)'
        }
        result = session.get(query, headers=headers)
        session.close()
        result = eval(result.content.decode())
        # print(result)
        if result['status'] == '1' and result['message'] == 'OK':
            return result['result']
        else:
            return None
    except Exception as e:
        print(e)
        return None
