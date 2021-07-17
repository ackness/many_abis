from .. import W_ERC20_ABI


SUPPORT_DEX = ['bakery', 'jul', 'mdex_bsc', 'pancake_v1', 'pancake_v2']


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

BASIC = {
    'chain': 'Binance Smart Chain',
    'explorer': 'https://bscscan.com/',
    'weth' : WETH,
    'coin': COINS
}
