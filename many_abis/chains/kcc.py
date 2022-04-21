from ._base import *

WKCS = BaseWETH(
    name='Wrapped KCS',
    symbol='WKCS',
    address='0x4446fc4eb47f2f6586f9faab68b3498f86c07521',
)

STABLE_COINS = BaseCoin(
    {
        'USDT': '0x0039f574ee5cc39bdd162e9a88e3eb1f111baf48',
        'USDC': '0x980a5afef3d17ad98635f6c5aebcbaeded3c3430'
    }
)

CHARTS = BaseChart(
    {
        'default': 'https://dexscreener.com/kcc/{lp_address}',
        'dexscreener': 'https://dexscreener.com/kcc/{lp_address}',
        'koffeeswap': 'https://koffeeswap.exchange/#/pro',
        'Sell/Buy On KoffeeSwap': 'https://koffeeswap.exchange/#/swap?outputCurrency={address}',
    }
)

RPC = BaseRPC(
    all=[
        'https://rpc-mainnet.kcc.network',
    ]
)

DEX = AttributeDict(
    koffeeswap=BaseDEX(
        name='KoffeeSwap', router_address='0xc0fFee0000C824D24E0F280f1e4D21152625742b',
        factory_address='0xC0fFeE00000e1439651C6aD025ea2A71ED7F3Eab', website='https://koffeeswap.exchange/',
    )
)

KCC = BaseChain(
    name='KuCoin Community Chain',
    explorer='https://explorer.kcc.io/en/',
    weth=WKCS,
    coins=STABLE_COINS,
    charts=CHARTS,
    rpcs=RPC,
    chain_id=321,
    dex=DEX,
)
