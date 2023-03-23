from ._base import *

WMATIC = BaseWETH(
    name='Wrapped Matic',
    symbol='WMATIC',
    address='0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270',
)

STABLE_COINS = BaseCoin(
    {
        'USDC': '0x2791bca1f2de4661ed88a30c99a7a9449aa84174',
        'DAI': '0x8f3cf7ad23cd3cadbd9735aff958023239c6a063',
        'PUSD': '0x9af3b7dc29d3c4b1a5731408b6a9656fa7ac3b72'
    }
)

CHARTS = BaseChart(
    {
        'default': 'https://dexscreener.com/polygon/{address}',
        'dexscreener': 'https://dexscreener.com/polygon/{address}',
        'poocoin': 'https://polygon.poocoin.app/tokens/{address}',
        'kek': 'https://kek.tools/t/{address}',
        'quickcharts': 'https://quickchart.app/token/{address}',
        'polychart': 'https://app.polychart.io/explorer/polygon/{address}',
        'dex.guru': 'https://dex.guru/token/{address}-polygon',
        'Sell/Buy On QuickSwap': 'https://quickswap.exchange/#/swap?outputCurrency={address}',
    }
)

RPC = BaseRPC(
    all=[
        'https://rpc-mainnet.matic.network',
        'https://rpc-mainnet.maticvigil.com',
        'https://rpc-mainnet.matic.quiknode.pro',
        'https://matic-mainnet.chainstacklabs.com',
        'https://matic-mainnet-full-rpc.bwarelabs.com',
        'https://matic-mainnet-archive-rpc.bwarelabs.com',
        'https://polygon.llamarpc.com',
        'https://polygon-rpc.com',
        'https://matic-mainnet.chainstacklabs.com',
        'https://poly-rpc.gateway.pokt.network',
        'https://rpc.ankr.com/polygon',
        'https://polygon-mainnet.public.blastapi.io',
        'https://1rpc.io/matic',
        'https://polygon-bor.publicnode.com',
        'https://polygon.blockpi.network/v1/rpc/public',
        'https://polygon.api.onfinality.io/public',
        'https://polygon.rpc.blxrbdn.com'
    ]
)

DEX = AttributeDict(
    quickswap=BaseDEX(
        name='QuickSwap', router_address='0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff',
        factory_address='0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32', website='https://quickswap.exchange/',
    )
)

POLYGON = BaseChain(
    name='Polygon PoS Chain',
    explorer='https://polygonscan.com/',
    weth=WMATIC,
    coins=STABLE_COINS,
    charts=CHARTS,
    rpcs=RPC,
    chain_id=137,
    dex=DEX,
)
