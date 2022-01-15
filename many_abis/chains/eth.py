from ._base import *

WETH = BaseWETH(
    name='Wrapped ETH',
    symbol='WETH',
    address='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
)

STABLE_COINS = BaseCoin(
    {
        'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
        'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        'DAI': '0x6B175474E89094C44Da98b954EedeAC495271d0F',
    }
)

CHARTS = BaseChart(
    {
        'default': 'https://www.dextools.io/app/uniswap/pair-explorer/{address}',
        'dextools': 'https://www.dextools.io/app/uniswap/pair-explorer/{address}',
        'Sell/Buy On Uniswap-V2': 'https://app.uniswap.org/#/swap?outputCurrency={address}&use=V2',
    }
)

RPC = BaseRPC(
    all=[
        'https://cloudflare-eth.com',
    ]
)

DEX = AttributeDict(
    uniswap_v2=BaseDEX(
        name='Uniswap V2', router_address='0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
        factory_address='0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f', website='https://app.uniswap.org/',
    )
)

ETH = BaseChain(
    name='Ethereum Chain',
    explorer='https://etherscan.io/',
    weth=WETH,
    coins=STABLE_COINS,
    charts=CHARTS,
    rpcs=RPC,
    chain_id=1,
    dex=DEX,
)
