from typing import Iterable, Mapping, Sequence


class WethMetaData:
    address: str
    name: str
    symbol: str


class SingleDexMetaData:
    factory_address: str
    router_address: str
    name: str
    website: str


class ChainMetaData:
    chain_id: int
    charts: Mapping[str, str]
    dex: Mapping[str, SingleDexMetaData]
    explorer: str
    name: str
    rpc: Sequence[str]
    stable_coins: Mapping[str, str]
    weth: WethMetaData


class ChainsMetaData:
    eth: ChainMetaData
    bsc: ChainMetaData
    polygon: ChainMetaData
    heco: ChainMetaData
    fantom: ChainMetaData
    arbitrum: ChainMetaData
    cronos: ChainMetaData
    avalanche: ChainMetaData
    kcc: ChainMetaData
    moonriver: ChainMetaData
    okx: ChainMetaData
    bsc_test: ChainMetaData
    optimism: ChainMetaData


class ABIMetaData(Iterable):
    AAVE_V1_ATOKEN: Sequence[Mapping]
    AAVE_V1_LENDING_POOL: Sequence[Mapping]
    AAVE_V1_LENDING_POOL_ADDRESSES_PROVIDER: Sequence[Mapping]
    AAVE_V1_LENDING_POOL_CORE: Sequence[Mapping]
    AAVE_V2_COLLECTOR: Sequence[Mapping]
    AAVE_V2_INCENTIVES_CONTROLLER: Sequence[Mapping]
    AAVE_V2_LENDING_POOL: Sequence[Mapping]
    AAVE_V2_LENDING_POOL_ADDRESSES_PROVIDER: Sequence[Mapping]
    AAVE_V2_LENDING_POOL_ADDRESSES_PROVIDER_REGISTRY: Sequence[Mapping]
    AAVE_V2_LENDING_POOL_COLLATERAL_MANAGER: Sequence[Mapping]
    AAVE_V2_LENDING_POOL_CONFIGURATOR: Sequence[Mapping]
    AAVE_V2_LENDING_RATE_ORACLE: Sequence[Mapping]
    AAVE_V2_POOL_ADMIN: Sequence[Mapping]
    AAVE_V2_PRICE_ORACLE: Sequence[Mapping]
    AAVE_V2_PROTOCAL_DATA_PROVIDER: Sequence[Mapping]
    AAVE_V2_UI_INCENTIVE_DATA_PROVIDER: Sequence[Mapping]
    AAVE_V2_UI_POOL_DATA_PROVIDER: Sequence[Mapping]
    AAVE_V2_WETH_GATEWAY: Sequence[Mapping]
    JOE_V2_FACTORY: Sequence[Mapping]
    JOE_V2_PAIR: Sequence[Mapping]
    JOE_V2_ROUTER: Sequence[Mapping]
    PANCAKE_V3_IPERIPHERY_PAYMENTS_WITH_FEE: Sequence[Mapping]
    PANCAKE_V3_MASTER_CHEF_V3: Sequence[Mapping]
    PANCAKE_V3_NON_FUNGIBLE_POSITION_MANAGER: Sequence[Mapping]
    PANCAKE_V3_POOL_V3: Sequence[Mapping]
    PANCAKE_V3_QUOTER: Sequence[Mapping]
    PANCAKE_V3_QUOTER_V2: Sequence[Mapping]
    PANCAKE_V3_ROUTER_V3: Sequence[Mapping]
    PANCAKE_V3_SELF_PERMIT: Sequence[Mapping]
    PANCAKE_V3_STAKER: Sequence[Mapping]
    UNISWAP_BSC_ROUTER: Sequence[Mapping]
    UNISWAP_V1_EXCHANGE: Sequence[Mapping]
    UNISWAP_V1_FACTORY: Sequence[Mapping]
    UNISWAP_V2_FACTORY: Sequence[Mapping]
    UNISWAP_V2_PAIR: Sequence[Mapping]
    UNISWAP_V2_ROUTER: Sequence[Mapping]
    UNISWAP_V3_FACTORY: Sequence[Mapping]
    UNISWAP_V3_MULTICALL: Sequence[Mapping]
    UNISWAP_V3_NON_FUNGIBLE_POSITION_MANAGE: Sequence[Mapping]
    UNISWAP_V3_POOL: Sequence[Mapping]
    UNISWAP_V3_QUOTER: Sequence[Mapping]
    UNISWAP_V3_ROUTER: Sequence[Mapping]
    ERC1155: Sequence[Mapping]
    ERC20: Sequence[Mapping]
    ERC721: Sequence[Mapping]
    ERC777: Sequence[Mapping]
    WETH9: Sequence[Mapping]
