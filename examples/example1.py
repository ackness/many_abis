import many_abis as ma

# ===================================
# chain, use upper str to access
chain = ma.get('BSC')

# for now, we collect this chains
support_chains = ma.SUPPORT_CHAIN
print(support_chains)
# ['BSC', 'ETH', 'AVAX', 'FANTOM', 'POLYGON', 'HECO', 'KCC', 'OKEX', 'MOONRIVER', 'ARBITRUM', 'BSC_TEST']

# print basic chain information
print(chain)
# Chain Name: Binance Smart Chain, Explorer: https://bscscan.com/, DEX: dict_keys(['pancake_v2', 'mdex_bsc', 'apeswap', 'biswap', 'jul'])

# all chain keys
print(chain.keys())
# dict_keys(['name', 'explorer', 'weth', 'coins', 'charts', 'rpcs', 'chain_id', 'dex'])

# you can use "." to access value
print(chain.coins)
# {'BUSD': '0xe9e7cea3dedca5984780bafc599bd69add087d56', 'USDT': '0x55d398326f99059ff775485246999027b3197955', 'USDC': '0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d'}

# you can also use dict like format
print(chain['weth'])
# {'name': 'Wrapped BNB', 'symbol': 'WBNB', 'address': '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c', 'abi': xxxx}

# ===================================
# dex, you should use upper str chain name, an lower str dex name
joe = ma.get('AVAX', 'joe')

# print basic dex information
print(joe)
# DEX Name: traderjoexyz, Website: https://traderjoexyz.com/#/home, Router: 0x60ae616a2155ee3d9a68541ba4544862310933d4, Factory: 0x9ad6c38be94206ca50bb0d90783181662f0cfa10

# all dex keys
print(joe.keys())
# dict_keys(['name', 'router_address', 'router_abi', 'factory_address', 'factory_abi', 'lp_abi', 'website'])

# use "." to access value
print(joe.router_address)

# use dict like format
print(joe['factory_address'])

# print all support dex
ma.print_all_dex()

bsc = ma.from_id(chain_id=56)
print(bsc)