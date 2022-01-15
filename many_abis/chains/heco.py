from ._base import *

WHT = BaseWETH(
    name='Wrapped HT',
    symbol='WHT',
    address='0x5545153CCFcA01fbd7Dd11C0b23ba694D9509A6F',
)

STABLE_COINS = BaseCoin(
    {
        'USDT HECO': '0xa71edc38d189767582c38a3145b5873052c3e47a',
        'USDC HECO': '0x9362bbef4b8313a8aa9f0c9808b80577aa26b73b',
        'DAI HECO': '0x3d760a45d0887dfd89a2f5385a236b29cb46ed2a'
    }
)

CHARTS = BaseChart(
    {
        'default': 'https://info.nut.money/token/{address}',
        'pippi': 'https://info.pippi.finance/token/{address}',  # only support
        'nut': 'https://info.nut.money/token/{address}',
        # xfarmer shold input pair address
        'xfarmer': 'https://xfarmer.net/trade.html?pair_address={address}',
        'Sell/Buy On MDEX-HECO': 'https://ht.mdex.co/#/swap?outputCurrency={address}',
    }
)

RPC = BaseRPC(
    all=[
        'https://http-mainnet.hecochain.com',  # other
        'https://http-mainnet-node.huobichain.com',  # china
        'https://http-mainnet-node.defibox.com',
    ]
)

DEX = AttributeDict(
    mdex_heco=BaseDEX(
        name='MDEX (HECO)', router_address='0xED7d5F38C79115ca12fe6C0041abb22F0A06C300',
        factory_address='0xb0b670fc1F7724119963018DB0BfA86aDb22d941', website='https://ht.mdex.co/#/swap/',
    )
)

HECO = BaseChain(
    name='Huobi Eco Chain',
    explorer='https://hecoinfo.com/',
    weth=WHT,
    coins=STABLE_COINS,
    charts=CHARTS,
    rpcs=RPC,
    chain_id=128,
    dex=DEX,
)
