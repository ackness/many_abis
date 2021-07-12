from dataclasses import dataclass


@dataclass(frozen=True)
class CHAIN_CONTRACT_API:
    ETH:str = 'https://api.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    ETH_CN:str = 'https://api-cn.etherscan.com/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    BSC:str = 'https://api.bscscan.com/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    HECO:str = 'https://api.hecoinfo.com/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    MATIC:str = 'https://api.polygonscan.com/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    KCC:str = '' # not support
