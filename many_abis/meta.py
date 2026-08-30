from typing import Any, Iterable, Mapping, Optional, Sequence


class WethMetaData(Mapping[str, Any]):
    address: str
    name: str
    symbol: str


class SingleDexMetaData(Mapping[str, Any]):
    deployment_source: Optional[str]
    factory_abi: Optional[str]
    factory_address: str
    router_address: str
    name: str
    protocol_family: Optional[str]
    protocol_version: Optional[str]
    router_abi: Optional[str]
    router_variant: Optional[str]
    status: Optional[str]
    website: str


class ChainMetaData(Mapping[str, Any]):
    chain_id: int
    charts: Mapping[str, str]
    dex: Mapping[str, SingleDexMetaData]
    explorer: str
    name: str
    rpc: Sequence[str]
    status: Optional[str]
    stable_coins: Mapping[str, str]
    test_coins: Optional[Mapping[str, str]]
    weth: WethMetaData


class ChainsMetaData(Mapping[str, ChainMetaData]):
    eth: ChainMetaData
    bsc: ChainMetaData
    base: ChainMetaData
    polygon: ChainMetaData
    sonic: ChainMetaData
    arbitrum: ChainMetaData
    cronos: ChainMetaData
    avalanche: ChainMetaData
    hyperevm: ChainMetaData
    monad: ChainMetaData
    robinhood: ChainMetaData
    unichain: ChainMetaData
    xlayer: ChainMetaData
    bsc_test: ChainMetaData
    optimism: ChainMetaData


class ABIMetaData(Iterable):
    AERODROME_SLIPSTREAM_V3_FACTORY: Sequence[Mapping]
    AERODROME_SLIPSTREAM_V3_ROUTER: Sequence[Mapping]
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
    LFJ_LIQUIDITY_BOOK_V2_2_FACTORY: Sequence[Mapping]
    LFJ_LIQUIDITY_BOOK_V2_2_ROUTER: Sequence[Mapping]
    PANCAKE_V3_BASE_FACTORY: Sequence[Mapping]
    PANCAKE_V3_FACTORY: Sequence[Mapping]
    PANCAKE_V3_IPERIPHERY_PAYMENTS_WITH_FEE: Sequence[Mapping]
    PANCAKE_V3_MASTER_CHEF_V3: Sequence[Mapping]
    PANCAKE_V3_NON_FUNGIBLE_POSITION_MANAGER: Sequence[Mapping]
    PANCAKE_V3_POOL_V3: Sequence[Mapping]
    PANCAKE_V3_QUOTER: Sequence[Mapping]
    PANCAKE_V3_QUOTER_V2: Sequence[Mapping]
    PANCAKE_V3_ROUTER_V3: Sequence[Mapping]
    PANCAKE_V3_SELF_PERMIT: Sequence[Mapping]
    PANCAKE_V3_SMART_ROUTER: Sequence[Mapping]
    PANCAKE_V3_STAKER: Sequence[Mapping]
    SHADOW_CLMM_V3_FACTORY: Sequence[Mapping]
    SHADOW_CLMM_V3_ROUTER: Sequence[Mapping]
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
    UNISWAP_V3_ROUTER_02: Sequence[Mapping]
    VELODROME_SLIPSTREAM_V3_FACTORY: Sequence[Mapping]
    VELODROME_SLIPSTREAM_V3_ROUTER: Sequence[Mapping]
    ERC1155: Sequence[Mapping]
    ERC20: Sequence[Mapping]
    ERC721: Sequence[Mapping]
    ERC777: Sequence[Mapping]
    WETH9: Sequence[Mapping]
