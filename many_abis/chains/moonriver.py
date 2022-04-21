from ._base import *

WMOVR = BaseWETH(
    name='Wrapped MOVR',
    symbol='WMOVR',
    address='0x98878B06940aE243284CA214f92Bb71a2b032B8A',
)

STABLE_COINS = BaseCoin(
    {
        'USDC': '0xE3F5a90F9cb311505cd691a46596599aA1A0AD7D',
        'DAI': '0x80A16016cC4A2E6a2CACA8a4a498b1699fF0f844',
    }
)

CHARTS = BaseChart(
    {
        'default': 'https://dexscreener.com/moonriver/{lp_address}',
        'dexscreener': 'https://dexscreener.com/moonriver/{lp_address}',
        'ChartEX': 'https://chartex.pro/dashboard',
        'Moonlit': 'https://moonlit.finance/',
        'Sell/Buy On Solarbeam': 'https://app.solarbeam.io/exchange/swap',
    }
)

RPC = BaseRPC(
    all=[
        'https://rpc.moonriver.moonbeam.network',
    ]
)

DEX = AttributeDict(
    solarbeam=BaseDEX(
        name='Solarbeam', router_address='0xAA30eF758139ae4a7f798112902Bf6d65612045f',
        factory_address='0x049581aEB6Fe262727f290165C29BDAB065a1B68', website='https://app.solarbeam.io/exchange/swap',
    )
)

MOONRIVER = BaseChain(
    name='Moonriver',
    explorer='https://moonriver.moonscan.io',
    weth=WMOVR,
    coins=STABLE_COINS,
    charts=CHARTS,
    rpcs=RPC,
    chain_id=1285,
    dex=DEX,
)
