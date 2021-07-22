from .. import W_ERC20_ABI


SUPPORT_DEX = ['koffeeswap']

WETH = {
    'name': 'Wrapped KCS',
    'symbol': 'WKCS',
    'address': '0x4446fc4eb47f2f6586f9faab68b3498f86c07521',
    'abi': W_ERC20_ABI,
}

COINS = {
    'USDT': '0x0039f574ee5cc39bdd162e9a88e3eb1f111baf48',
    'USDC': '0x980a5afef3d17ad98635f6c5aebcbaeded3c3430'
}

CHARTS = {
    'default': 'https://koffeeswap.exchange/#/pro',
    'koffeeswap': 'https://koffeeswap.exchange/#/pro',
    'Sell/Buy On KoffeeSwap': 'https://koffeeswap.exchange/#/swap?outputCurrency={address}',
}

RPC = [
    'https://rpc-mainnet.kcc.network',
]

BASIC = {
    'chain': 'KuCoin Community Chain',
    'explorer': 'https://explorer.kcc.io/en/',
    'weth' : WETH,
    'coins': COINS,
    'charts': CHARTS,
    'rpc': RPC,
}
