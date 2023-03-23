from ._base import *

WBNB = BaseWETH(
    name='Wrapped BNB',
    symbol='WBNB',
    address='0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd',
)

STABLE_COINS = BaseCoin(
    {
        'BUSD': '0xeD24FC36d5Ee211Ea25A80239Fb8C4Cfd80f12Ee',
        'USDT': '0x337610d27c682E347C9cD60BD4b3b107C9d34dDd',
        'USDC': '0x64544969ed7EBf5f083679233325356EbE738930',
    }
)

# https://testnet.bscscan.com/address/0xaa25aa7a19f9c426e07dee59b12f944f4d9f1dd3#tokentxns
TEST_COINS = {
    'BTCB': '0x6ce8dA28E2f864420840cF74474eFf5fD80E65B8',
    'ETH': '0xd66c6B4F0be8CE5b39D52E0Fd1344c389929B378',
    'XRP': '0xa83575490D7df4E2F47b7D38ef351a2722cA45b9'
}

CHARTS = BaseChart(
    {
        'default': 'https://test-binance-chain-charts/this-is-not-real-url/{address}',
        'Sell/Buy On UNREAL SWAP': 'https://test-binance-chain-swap/this-is-not-real-url/{address}/#/swap?outputCurrency={address}',
    }
)

RPC = BaseRPC(
    all=[
        'https://data-seed-prebsc-1-s1.binance.org:8545/',
        'https://data-seed-prebsc-2-s1.binance.org:8545/',
        'https://data-seed-prebsc-1-s2.binance.org:8545/',
        'https://data-seed-prebsc-2-s2.binance.org:8545/',
        'https://data-seed-prebsc-1-s3.binance.org:8545/',
        'https://data-seed-prebsc-2-s3.binance.org:8545/',
        'https://bsc-testnet.public.blastapi.io',
    ]
)

DEX = AttributeDict(
    pancake_v2_test=BaseDEX(
        name='PancakeSwap v2 (TEST)', router_address='0xD99D1c33F9fC3444f8101754aBC46c52416550D1',
        factory_address='0x6725F303b657a9451d8BA641348b6761A6CC7a17', website=''
    ),
)

BSC_TEST = BaseChain(
    name='Binance Smart Chain Testnet',
    explorer='https://testnet.bscscan.com/',
    weth=WBNB,
    coins=STABLE_COINS,
    charts=CHARTS,
    rpcs=RPC,
    chain_id=97,
    dex=DEX,
)
