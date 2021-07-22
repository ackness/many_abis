from .. import W_ERC20_ABI


SUPPORT_DEX = ['uniswap_v2']

WETH = {
    'name': 'Wrapped Ether',
    'symbol': 'WETH',
    'address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    'abi': W_ERC20_ABI,
}

COINS = {
    'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
    'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    'DAI': '0x6B175474E89094C44Da98b954EedeAC495271d0F',
}

CHARTS = {
    'default': 'https://www.dextools.io/app/uniswap/pair-explorer/{address}',
    'dextools': 'https://www.dextools.io/app/uniswap/pair-explorer/{address}',
    'Sell/Buy On Uniswap-V2': 'https://app.uniswap.org/#/swap?outputCurrency={address}&use=V2',
}

RPC = [
    'https://cloudflare-eth.com',
]

BASIC = {
    'chain': 'Ethereum Chain',
    'explorer': 'https://etherscan.io/',
    'weth' : WETH,
    'coins': COINS,
    'charts': CHARTS,
    'rpc': RPC,
}

