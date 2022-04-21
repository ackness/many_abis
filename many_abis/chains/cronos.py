from ._base import *

WCRO = BaseWETH(
    name='Wrapped CRO',
    symbol='WCRO',
    address='0x5C7F8A570d578ED84E63fdFA7b1eE72dEae1AE23',
)

STABLE_COINS = BaseCoin(
    {
        'DAI': '0xF2001B145b43032AAF5Ee2884e456CCd805F677D',
        'USDC': '0xc21223249CA28397B4B6541dfFaEcC539BfF0c59',
        'USDT': '0x66e428c3f67a68878562e79A0234c1F83c208770',
    }
)

CHARTS = BaseChart(
    {
        'default': 'https://dexscreener.com/cronos/{lp_address}',
        'dexscreener': 'https://dexscreener.com/cronos/{lp_address}',
        'Sell/Buy On MMF': 'https://mm.finance/swap?outputCurrency={address}',
    }
)

RPC = BaseRPC(
    all=[
        'https://evm-cronos.crypto.org',  
        'https://evm.cronos.org', 
        'https://cronosrpc-1.xstaking.sg',
        'https://cronos-rpc.elk.finance'
    ]
)

DEX = AttributeDict(
    mmf=BaseDEX(
        name='Mad Meerkat Finance', router_address='0x145677FC4d9b8F19B5D56d1820c48e0443049a30',
        factory_address='0xd590cC180601AEcD6eeADD9B7f2B7611519544f4', website='https://mm.finance/swap',
    )
)

CRONOS = BaseChain(
    name='Cronos Mainnet',
    explorer='https://cronoscan.com/',
    weth=WCRO,
    coins=STABLE_COINS,
    charts=CHARTS,
    rpcs=RPC,
    chain_id=25,
    dex=DEX,
)
