import many_abis as ma

# ===================================
# get abis


# ===================================
# chains
chains = ma.all_chains()
print(chains)
# ['arbitrum-one', 'avax-c', 'bsc', 'bsc-test', 'cronos', 'eth', 'fantom', 'heco', 'kcc', 'moonriver', 'okex', 'polygon']

bsc = ma.get_chain_by_id(chain_id=56)
bsc = ma.get_chain_by_name(name="bsc")
bsc = ma.get_chain(name="bsc")
bsc = ma.get_chain(chain_id=56)
bsc = ma.chain(name="bsc")
bsc = ma.chain(chain_id=56)
print(bsc)

ds = ma.get('bsc', 'dex', 'pancake_v2')
print(ds)
# {'factory_address': '0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73', 'name': 'PancakeSwap v2', 'router_address': '0x10ED43C718714eb63d5aA57B78B54704E256024E', 'website': 'https://pancakeswap.finance/swap'}
