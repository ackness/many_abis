from .. import W_ERC20_ABI


SUPPORT_DEX = ['bakery', 'jul', 'mdex_bsc', 'pancake_v1', 'pancake_v2', 'apeswap']


WETH = {
    'name': 'Wrapped BNB',
    'symbol': 'WBNB',
    'address': '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
    'abi': W_ERC20_ABI,
}

COINS = {
    'BUSD': '0xe9e7cea3dedca5984780bafc599bd69add087d56',
    'USDT': '0x55d398326f99059ff775485246999027b3197955',
    'USDC': '0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d',
}

CHARTS = {
    'default': 'https://poocoin.app/tokens/{address}',
    'poocoin': 'https://poocoin.app/tokens/{address}',
    'dextools': 'https://www.dextools.io/app/pancakeswap/pair-explorer/{address}',
    'dex.guru': 'https://dex.guru/token/{address}-bsc',
    'bogged': 'https://charts.bogged.finance/?token={address}',
    'avedex':'https://avedex.org/token/{address}',
    'Sell/Buy On Pancake-V2': 'https://exchange.pancakeswap.finance/#/swap?outputCurrency={address}',
}

RPC = [
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

BASIC = {
    'chain': 'Binance Smart Chain',
    'explorer': 'https://bscscan.com/',
    'weth' : WETH,
    'coins': COINS,
    'charts': CHARTS,
    'rpc': RPC
}
