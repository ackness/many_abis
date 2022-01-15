from dataclasses import dataclass


@dataclass(frozen=True)
class CHAIN_SCAN_API:
    ETH: str = 'https://api.etherscan.io/api'
    ETH_CN: str = 'https://api-cn.etherscan.com/api'
    BSC: str = 'https://api.bscscan.com/api'
    HECO: str = 'https://api.hecoinfo.com/api'
    MATIC: str = 'https://api.polygonscan.com/api?'
    FTM: str = 'https://api.ftmscan.com/api'
    MOONRIVER: str = 'https://api-moonriver.moonscan.io/api'
    AVAX: str = 'https://api.snowtrace.io/api'  # showtrace
    KCC: str = ''  # not supported
    ARBITRUM: str = 'https://api.arbiscan.io/'
