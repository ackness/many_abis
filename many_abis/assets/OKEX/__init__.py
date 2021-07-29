from .. import W_ERC20_ABI


SUPPORT_DEX = ['pandaex', 'cherryswap', 'jswap']

WETH = {
    'name': 'Wrapped OKT',
    'symbol': 'WOKT',
    'address': '0x8f8526dbfd6e38e3d8307702ca8469bae6c56c15',
    'abi': W_ERC20_ABI,
}

COINS = {
    'USDT': '0x382bb369d343125bfb2117af9c149795c6c65c50',
    'USDC': '0xc946daf81b08146b1c7a8da2a851ddf2b3eaaf85',
}

CHARTS = {
    'default': 'https://www.cherryswap.net/#/swap?outputCurrency={address}',
    'Sell/Buy On CherrySwap': 'https://www.cherryswap.net/#/swap?outputCurrency={address}',
    'Sell/Buy On JSwap': 'https://app.jswap.finance/#/swap?outputCurrency={address}',
    'Sell/Buy On Pandaex': 'https://app.pandaex.org/#/swap?outputCurrency={address}',
}

RPC = [
    'https://exchainrpc.okex.org',
]

BASIC = {
    'chain': 'OKExChain',
    'explorer': 'https://www.oklink.com/okexchain/',
    'weth' : WETH,
    'coins': COINS,
    'charts': CHARTS,
    'rpc': RPC,
}