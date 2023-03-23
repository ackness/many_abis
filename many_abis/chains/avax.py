from ._base import *

WAVAX = BaseWETH(
    name='Wrapped AVAX',
    symbol='WAVAX',
    address='0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7',
)

# from https://snowtrace.io/tokens
STABLE_COINS = BaseCoin(
    {
        'USDT.e': '0xc7198437980c041c805A1EDcbA50c1Ce5db95118',
        'USDC.e': '0xA7D7079b0FEaD91F3e65f86E8915Cb59c1a4C664',
        'Dai.e': '0xd586E7F844cEa2F87f50152665BCbc2C279D8d70',
    }
)

CHARTS = BaseChart(
    {
        'default': 'https://dexscreener.com/avalanche/{lp_address}',
        'ChartEX': 'https://chartex.pro/dashboard',
        'dexscreener': 'https://dexscreener.com/avalanche/{lp_address}',
        'Sell/Buy On traderjoexyz': 'https://traderjoexyz.com/#/trade',
    }
)

RPC = BaseRPC(
    all=[
        'https://api.avax.network/ext/bc/C/rpc',
        'https://avalanche.public-rpc.com',
        'https://rpc.ankr.com/avalanche',
        'https://ava-mainnet.public.blastapi.io/ext/bc/C/rpc',
        'https://avalanche-c-chain.publicnode.com',
        'https://1rpc.io/avax/c',
        'https://avalanche.blockpi.network/v1/rpc/public'
    ]
)

DEX = AttributeDict(
    joe=BaseDEX(
        name='traderjoexyz', router_address='0x60ae616a2155ee3d9a68541ba4544862310933d4',
        router_abi=AVAX_JOE_ROUTER_ABI, factory_address='0x9ad6c38be94206ca50bb0d90783181662f0cfa10',
        factory_abi=AVAX_JOE_FACTORY_ABI, lp_abi=AVAX_JOE_PAIR_ABI, website='https://traderjoexyz.com/#/home',
    )
)

AVAX = BaseChain(
    name='Avalanche Network',
    explorer='https://snowtrace.io/',
    weth=WAVAX,
    coins=STABLE_COINS,
    charts=CHARTS,
    rpcs=RPC,
    chain_id=43114,
    dex=DEX,
)
