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
    AAVE_V2_LENDING_POOL_ADDRESSES_PROVIDER: Sequence[Mapping]
    AERODROME_SLIPSTREAM_V3_FACTORY: Sequence[Mapping]
    AERODROME_SLIPSTREAM_V3_ROUTER: Sequence[Mapping]
    CHAINLINK_AGGREGATOR_V3: Sequence[Mapping]
    ERC1271: Sequence[Mapping]
    ERC165: Sequence[Mapping]
    ERC20_PERMIT: Sequence[Mapping]
    ERC2981: Sequence[Mapping]
    ERC4626: Sequence[Mapping]
    ERC5267: Sequence[Mapping]
    ERC6093_ERC1155_ERRORS: Sequence[Mapping]
    ERC6093_ERC20_ERRORS: Sequence[Mapping]
    ERC6093_ERC721_ERRORS: Sequence[Mapping]
    ERC6909: Sequence[Mapping]
    ERC6909_METADATA: Sequence[Mapping]
    LFJ_LIQUIDITY_BOOK_V2_2_FACTORY: Sequence[Mapping]
    LFJ_LIQUIDITY_BOOK_V2_2_ROUTER: Sequence[Mapping]
    MULTICALL3: Sequence[Mapping]
    OPENZEPPELIN_ACCESS_CONTROL_V5: Sequence[Mapping]
    OPENZEPPELIN_IERC1967: Sequence[Mapping]
    PANCAKE_V3_BASE_FACTORY: Sequence[Mapping]
    PANCAKE_V3_FACTORY: Sequence[Mapping]
    PANCAKE_V3_POOL_V3: Sequence[Mapping]
    PANCAKE_V3_ROUTER_V3: Sequence[Mapping]
    PANCAKE_V3_SMART_ROUTER: Sequence[Mapping]
    SHADOW_CLMM_V3_FACTORY: Sequence[Mapping]
    SHADOW_CLMM_V3_ROUTER: Sequence[Mapping]
    UNISWAP_PERMIT2: Sequence[Mapping]
    UNISWAP_V1_EXCHANGE: Sequence[Mapping]
    UNISWAP_V2_FACTORY: Sequence[Mapping]
    UNISWAP_V2_ROUTER: Sequence[Mapping]
    UNISWAP_V3_FACTORY: Sequence[Mapping]
    UNISWAP_V3_POOL_EVENTS: Sequence[Mapping]
    UNISWAP_V3_POOL_STATE: Sequence[Mapping]
    UNISWAP_V3_ROUTER_02: Sequence[Mapping]
    VELODROME_SLIPSTREAM_V3_FACTORY: Sequence[Mapping]
    VELODROME_SLIPSTREAM_V3_ROUTER: Sequence[Mapping]
