from ._base import *

WBNB = BaseWETH(
    name='Wrapped BNB',
    symbol='WBNB',
    address='0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
)

STABLE_COINS = BaseCoin(
    {
        'BUSD': '0xe9e7cea3dedca5984780bafc599bd69add087d56',
        'USDT': '0x55d398326f99059ff775485246999027b3197955',
        'USDC': '0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d',
    }
)

CHARTS = BaseChart(
    {
        'default': 'https://poocoin.app/tokens/{address}',
        'poocoin': 'https://poocoin.app/tokens/{address}',
        'dextools': 'https://www.dextools.io/app/pancakeswap/pair-explorer/{address}',
        'dex.guru': 'https://dex.guru/token/{address}-bsc',
        'bogged': 'https://charts.bogged.finance/?token={address}',
        'avedex': 'https://avedex.org/token/{address}',
        'dexscreener': 'https://dexscreener.com/bsc/{lp_address}',
        'Sell/Buy On Pancake-V2': 'https://exchange.pancakeswap.finance/#/swap?outputCurrency={address}',
    }
)

RPC = BaseRPC(
    all=[
        'https://bsc-dataseed.binance.org/',
        'https://bsc-dataseed1.binance.org/',
        'https://bsc-dataseed2.binance.org/',
        'https://bsc-dataseed3.binance.org/',
        'https://bsc-dataseed4.binance.org/',
        'https://bsc-dataseed1.defibit.io/',
        'https://bsc-dataseed2.defibit.io/',
        'https://bsc-dataseed3.defibit.io/',
        'https://bsc-dataseed4.defibit.io/',
        'https://bsc-dataseed1.ninicoin.io/',
        'https://bsc-dataseed2.ninicoin.io/',
        'https://bsc-dataseed3.ninicoin.io/',
        'https://bsc-dataseed4.ninicoin.io/',
    ]
)

DEX = AttributeDict(
    pancake_v2=BaseDEX(
        name='PancakeSwap v2', router_address='0x10ED43C718714eb63d5aA57B78B54704E256024E',
        factory_address='0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73',
        website='https://exchange.pancakeswap.finance/#/swap'
    ),
    mdex_bsc=BaseDEX(
        name='MDEX (BSC)', router_address='0x7DAe51BD3E3376B8c7c4900E9107f12Be3AF1bA8',
        factory_address='0x3CD1C46068dAEa5Ebb0d3f55F6915B10648062B8', website='https://bsc.mdex.co/#/swap/'
    ),
    apeswap=BaseDEX(
        name='ApeSwap Finance', router_address='0xcF0feBd3f17CEf5b47b0cD257aCf6025c5BFf3b7',
        factory_address='0x0841BD0B734E4F5853f0dD8d7Ea041c241fb0Da6', website='https://app.apeswap.finance/swap'
    ),
    biswap=BaseDEX(
        name='BiSwap', router_address='0x3a6d8cA21D1CF76F653A67577FA0D27453350dD8',
        factory_address='0x858E3312ed3A876947EA49d572A7C42DE08af7EE', website='https://exchange.biswap.org/#/swap'
    ),
    # bakery=BaseDEX(
    #     name='BakerySwap', router_address='0xBf6527834dBB89cdC97A79FCD62E6c08B19F8ec0', router_abi=BAKERY_ROUTER_ABI, factory_address='0x8a1E9d3aEbBBd5bA2A64d3355A48dD5E9b511256', factory_abi=BAKERY_FACTORY_ABI, website='https://www.bakeryswap.org/'),
    jul=BaseDEX(
        name='Just Liquidity', router_address='0xbd67d157502A23309Db761c41965600c2Ec788b2',
        factory_address='0x553990F2CBA90272390f62C5BDb1681fFc899675', website='https://dexbeta.julswap.com/'
    )
)

BSC = BaseChain(
    name='Binance Smart Chain',
    explorer='https://bscscan.com/',
    weth=WBNB,
    coins=STABLE_COINS,
    charts=CHARTS,
    rpcs=RPC,
    chain_id=56,
    dex=DEX,
)
