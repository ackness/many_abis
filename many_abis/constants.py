from dataclasses import dataclass


@dataclass(frozen=True)
class CHAIN_SCAN_API:
    ETH: str = 'https://api.etherscan.io/api'
    ETH_CN: str = 'https://api-cn.etherscan.com/api'
    BSC: str = 'https://api.bscscan.com/api'
    HECO: str = 'https://api.hecoinfo.com/api'
    MATIC: str = 'https://api.polygonscan.com/api'
    FTM: str = 'https://api.ftmscan.com/api'
    MOONRIVER: str = 'https://api-moonriver.moonscan.io/api'
    AVAX: str = 'https://api.snowtrace.io/api'  # showtrace
    KCC: str = ''  # not supported
    ARBITRUM: str = 'https://api.arbiscan.io/'
    CRONOS: str = 'https://api.cronoscan.com/api'
    OPT: str = 'https://api-optimistic.etherscan.io/api'


@dataclass(frozen=True)
class CHAIN_CONTRACT_API:
    ETH: str = 'https://api.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    ETH_CN: str = 'https://api-cn.etherscan.com/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    BSC: str = 'https://api.bscscan.com/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    HECO: str = 'https://api.hecoinfo.com/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    MATIC: str = 'https://api.polygonscan.com/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    FTM: str = 'https://api.ftmscan.com/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    MOONRIVER: str = 'https://api-moonriver.moonscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    # showtrace
    AVAX: str = 'https://api.snowtrace.io/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    KCC: str = ''  # not support
    ARBITRUM: str = 'https://api.arbiscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    CRONOS: str = 'https://api.cronoscan.com/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    OPT: str = 'https://api-optimistic.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
