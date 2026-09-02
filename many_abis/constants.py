from dataclasses import dataclass


ETHERSCAN_V2_API = "https://api.etherscan.io/v2/api"


def _contract_api(chain_id: int) -> str:
    return (
        ETHERSCAN_V2_API
        + "?chainid={}&module=contract&action=getabi"
        "&address={{contract_address}}&apikey={{api_key}}".format(chain_id)
    )


@dataclass(frozen=True)
class CHAIN_SCAN_API:
    """Deprecated per-chain aliases for the single Etherscan V2 endpoint."""

    ETH: str = ETHERSCAN_V2_API
    ETH_CN: str = ETHERSCAN_V2_API
    BSC: str = ETHERSCAN_V2_API
    MATIC: str = ETHERSCAN_V2_API
    AVAX: str = ETHERSCAN_V2_API
    ARBITRUM: str = ETHERSCAN_V2_API
    CRONOS: str = ETHERSCAN_V2_API
    OPT: str = ETHERSCAN_V2_API


@dataclass(frozen=True)
class ETHERSCAN_CHAIN_ID:
    ETH: int = 1
    ETH_CN: int = 1
    BSC: int = 56
    MATIC: int = 137
    AVAX: int = 43114
    ARBITRUM: int = 42161
    CRONOS: int = 25
    OPT: int = 10


@dataclass(frozen=True)
class CHAIN_CONTRACT_API:
    """Deprecated templates accepted only as trusted chain selectors.

    ``get_abi_from_address`` never requests these formatted strings. It maps an
    exact known template to a chain ID, then calls ``ETHERSCAN_V2_API`` with
    structured query parameters.
    """

    ETH: str = _contract_api(ETHERSCAN_CHAIN_ID.ETH)
    ETH_CN: str = _contract_api(ETHERSCAN_CHAIN_ID.ETH_CN)
    BSC: str = _contract_api(ETHERSCAN_CHAIN_ID.BSC)
    MATIC: str = _contract_api(ETHERSCAN_CHAIN_ID.MATIC)
    AVAX: str = _contract_api(ETHERSCAN_CHAIN_ID.AVAX)
    ARBITRUM: str = _contract_api(ETHERSCAN_CHAIN_ID.ARBITRUM)
    CRONOS: str = _contract_api(ETHERSCAN_CHAIN_ID.CRONOS)
    OPT: str = _contract_api(ETHERSCAN_CHAIN_ID.OPT)


_CHAIN_API_TO_ID = {
    CHAIN_CONTRACT_API.ETH: ETHERSCAN_CHAIN_ID.ETH,
    CHAIN_CONTRACT_API.BSC: ETHERSCAN_CHAIN_ID.BSC,
    CHAIN_CONTRACT_API.MATIC: ETHERSCAN_CHAIN_ID.MATIC,
    CHAIN_CONTRACT_API.AVAX: ETHERSCAN_CHAIN_ID.AVAX,
    CHAIN_CONTRACT_API.ARBITRUM: ETHERSCAN_CHAIN_ID.ARBITRUM,
    CHAIN_CONTRACT_API.CRONOS: ETHERSCAN_CHAIN_ID.CRONOS,
    CHAIN_CONTRACT_API.OPT: ETHERSCAN_CHAIN_ID.OPT,
    # Exact pre-V2 constants remain accepted as migration-only selectors. They
    # are never used as request URLs.
    "https://api.etherscan.io/api?module=contract&action=getabi&address="
    "{contract_address}&apikey={api_key}": ETHERSCAN_CHAIN_ID.ETH,
    "https://api-cn.etherscan.com/api?module=contract&action=getabi&address="
    "{contract_address}&apikey={api_key}": ETHERSCAN_CHAIN_ID.ETH_CN,
    "https://api.bscscan.com/api?module=contract&action=getabi&address="
    "{contract_address}&apikey={api_key}": ETHERSCAN_CHAIN_ID.BSC,
    "https://api.polygonscan.com/api?module=contract&action=getabi&address="
    "{contract_address}&apikey={api_key}": ETHERSCAN_CHAIN_ID.MATIC,
    "https://api.snowtrace.io/api?module=contract&action=getabi&address="
    "{contract_address}&apikey={api_key}": ETHERSCAN_CHAIN_ID.AVAX,
    "https://api.arbiscan.io/api?module=contract&action=getabi&address="
    "{contract_address}&apikey={api_key}": ETHERSCAN_CHAIN_ID.ARBITRUM,
    "https://api.cronoscan.com/api?module=contract&action=getabi&address="
    "{contract_address}&apikey={api_key}": ETHERSCAN_CHAIN_ID.CRONOS,
    "https://api-optimistic.etherscan.io/api?module=contract&action=getabi&address="
    "{contract_address}&apikey={api_key}": ETHERSCAN_CHAIN_ID.OPT,
}
