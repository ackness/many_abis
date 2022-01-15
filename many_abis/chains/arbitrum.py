from ._base import *

WETH = BaseWETH(
    name='Wrapped ETH',
    symbol='WETH',
    address='0x82aF49447D8a07e3bd95BD0d56f35241523fBab1',
)

STABLE_COINS = BaseCoin(
    {
        'USDT': '0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9',
        'USDC': '0xff970a61a04b1ca14834a43f5de4533ebddb5cc8'
    }
)

CHARTS = BaseChart(
    {
        'default': 'https://app.sushi.com/en/swap',
        'SushiSwap': 'https://app.sushi.com/en/swap',
        'Sell/Buy On SushiSwap': 'https://app.sushi.com/en/swap',
    }
)

RPC = BaseRPC(
    all=[
        'https://arb1.arbitrum.io/rpc',
    ]
)

DEX = AttributeDict(
    suhiswap=BaseDEX(
        name='SushiSwap', router_address='0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506',
        factory_address='0xc35DADB65012eC5796536bD9864eD8773aBc74C4', website='https://app.sushi.com/en/swap',
    )
)

ARBITRUM = BaseChain(
    name='Arbitrum One',
    explorer='https://arbiscan.io',
    weth=WETH,
    coins=STABLE_COINS,
    charts=CHARTS,
    rpcs=RPC,
    chain_id=42161,
    dex=DEX,
)
