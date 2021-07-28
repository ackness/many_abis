from dataclasses import dataclass


@dataclass(frozen=True)
class CHAIN_RPC_API:
    ETH:str = 'https://cloudflare-eth.com'
    BSC:str = 'https://bsc-dataseed1.defibit.io' 
    HECO:str = 'https://http-mainnet-node.huobichain.com'
    MATIC:str = 'https://rpc-mainnet.maticvigil.com'
    KCC:str = 'https://rpc-mainnet.kcc.network'
    OKEX:str = 'https://exchainrpc.okex.org'
