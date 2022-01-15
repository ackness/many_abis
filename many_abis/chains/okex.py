from ._base import *

WOKT = BaseWETH(
    name='Wrapped OKT',
    symbol='WOKT',
    address='0x8f8526dbfd6e38e3d8307702ca8469bae6c56c15',
)

STABLE_COINS = BaseCoin(
    {
        'USDT': '0x382bb369d343125bfb2117af9c149795c6c65c50',
        'USDC': '0xc946daf81b08146b1c7a8da2a851ddf2b3eaaf85',
    }
)

CHARTS = BaseChart(
    {
        'default': 'https://www.cherryswap.net/#/swap?outputCurrency={address}',
        'Sell/Buy On CherrySwap': 'https://www.cherryswap.net/#/swap?outputCurrency={address}',
        'Sell/Buy On JSwap': 'https://app.jswap.finance/#/swap?outputCurrency={address}',
        'Sell/Buy On Pandaex': 'https://app.pandaex.org/#/swap?outputCurrency={address}',
    }
)

RPC = BaseRPC(
    all=[
        'https://exchainrpc.okex.org',
    ]
)

DEX = AttributeDict(
    cherryswap=BaseDEX(
        name='CherrySwap', router_address='0x865bfde337C8aFBffF144Ff4C29f9404EBb22b15',
        factory_address='0x709102921812B3276A65092Fe79eDfc76c4D4AFe', website='https://www.cherryswap.net/',
    ),

    jswap=BaseDEX(
        name='JSwap', router_address='0x069A306A638ac9d3a68a6BD8BE898774C073DCb3',
        factory_address='0xd654CbF99F2907F06c88399AE123606121247D5C', website='https://app.jswap.finance/',
    ),
    pandaswap=BaseDEX(
        name='PandaSwap', router_address='0x6eC2A127057c13Dff1D04e0ae131a756aa4033d4',
        factory_address='0x328C72A24d63E3d903ba9272B95A23ec919eB7E1', website='https://app.pandaex.org/',
    )
)

OKEX = BaseChain(
    name='OKExChain',
    explorer='https://www.oklink.com/okexchain/',
    weth=WOKT,
    coins=STABLE_COINS,
    charts=CHARTS,
    rpcs=RPC,
    chain_id=66,
    dex=DEX,
)
