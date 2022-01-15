from ._base import *

WFTM = BaseWETH(
    name='Wrapped Fantom Token',
    symbol='WFTM',
    address='0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83',
)

STABLE_COINS = BaseCoin(
    {
        'USDC': '0x04068DA6C83AFCFA0e13ba15A6696662335D5B75',
        'DAI': '0x8D11eC38a3EB5E956B052f67Da8Bdc9bef8Abf3E',
    }
)

CHARTS = BaseChart(
    {
        'ChartEX': 'https://chartex.pro/dashboard',
        'Sell/Buy On SpookySwap': 'https://spookyswap.finance/swap',
        'Sell/Buy On SpiritSwap': 'https://swap.spiritswap.finance/#/exchange/swap/{address}',
    }
)

RPC = BaseRPC(
    all=[
        'https://rpc.ftm.tools',
    ]
)

DEX = AttributeDict(
    spookyswap=BaseDEX(
        name='SpookySwap', router_address='0xF491e7B69E4244ad4002BC14e878a34207E38c29',
        factory_address='0x152eE697f2E276fA89E96742e9bB9aB1F2E61bE3', website='https://spookyswap.finance/',
    ),
    spiritswap=BaseDEX(
        name='SpiritSwap', router_address='0x16327E3FbDaCA3bcF7E38F5Af2599D2DDc33aE52',
        factory_address='0xEF45d134b73241eDa7703fa787148D9C9F4950b0', website='https://www.spiritswap.finance/',
    ),
)

FANTOM = BaseChain(
    name='Fantom Opera',
    explorer='https://ftmscan.com/',
    weth=WFTM,
    coins=STABLE_COINS,
    charts=CHARTS,
    rpcs=RPC,
    chain_id=250,
    dex=DEX,
)
