import many_abis as ma

# ======================================================================
# get all abi names
print(ma.ALL_ABIS_NAME)

# get all abis
print(ma.ABIS)

# you can access ABI by dot name
print(ma.ABIS.ERC20)


# ======================================================================
# get abi from address using etherscan api
ma.get_abi_from_address(
    "0x0841BD0B734E4F5853f0dD8d7Ea041c241fb0Da6",
    "YOUR API KEY",
    ma.CHAIN_CONTRACT_API.BSC
)

# ======================================================================
# chains
chains = ma.all_chains()
print(chains)
# ['arbitrum-one', 'avax-c', 'bsc', 'bsc-test', 'cronos', 'eth', 'fantom', 'heco', 'kcc', 'moonriver', 'okex', 'polygon']

# different methods to get chain
bsc = ma.get_chain_by_id(chain_id=56)
bsc = ma.get_chain_by_name(name="bsc")
bsc = ma.get_chain(name="bsc")
bsc = ma.get_chain(chain_id=56)
bsc = ma.chain(name="bsc")
bsc = ma.chain(chain_id=56)
print(bsc)

# to get some items from chain
eth_weth = ma.get('eth', 'weth')
print(eth_weth)
# {'address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'name': 'Wrapped ETH', 'symbol': 'WETH'}

ds = ma.get('bsc', 'dex', 'pancake_v2')
print(ds)
# {'factory_address': '0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73', 'name': 'PancakeSwap v2', 'router_address': '0x10ED43C718714eb63d5aA57B78B54704E256024E', 'website': 'https://pancakeswap.finance/swap'}
