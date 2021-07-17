from .. import W_ERC20_ABI


SUPPORT_DEX = ['quickswap']

WETH = {
    'name': 'Wrapped Matic',
    'symbol': 'WMATIC',
    'address': '0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270',
    'abi': W_ERC20_ABI,
}

COINS = {
    'USDC': '0x2791bca1f2de4661ed88a30c99a7a9449aa84174',
    'DAI': '0x8f3cf7ad23cd3cadbd9735aff958023239c6a063',
    'PUSD': '0x9af3b7dc29d3c4b1a5731408b6a9656fa7ac3b72'
}

BASIC = {
    'chain': 'Polygon PoS Chain',
    'explorer': 'https://polygonscan.com/',
    'weth' : WETH,
    'coin': COINS
}