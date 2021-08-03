from dataclasses import dataclass


@dataclass(frozen=True)
class CHAIN_SCAN_API:
    ETH:str = 'https://api.etherscan.io/api?module='
    ETH_CN:str = 'https://api-cn.etherscan.com/api?module='
    BSC:str = 'https://api.bscscan.com/api?module='
    HECO:str = 'https://api.hecoinfo.com/api?module='
    MATIC:str = 'https://api.polygonscan.com/api?module='
    KCC:str = ''  # not supported 

