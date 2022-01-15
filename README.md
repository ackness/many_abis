# Many Abis [v0.1.0]

Get different DEX abis easily for blockchain developers.

---

Now we support dex: 

---

- BSC:
	- [1] [PancakeSwap v2](https://exchange.pancakeswap.finance/#/swap)
	- [2] [MDEX (BSC)](https://bsc.mdex.co/#/swap/)
	- [3] [ApeSwap Finance](https://app.apeswap.finance/swap)
	- [4] [BiSwap](https://exchange.biswap.org/#/swap)
	- [5] [Just Liquidity](https://dexbeta.julswap.com/)
- ETH:
	- [1] [Uniswap V2](https://app.uniswap.org/)
- AVAX:
	- [1] [traderjoexyz](https://traderjoexyz.com/#/home)
- FANTOM:
	- [1] [SpookySwap](https://spookyswap.finance/)
	- [2] [SpiritSwap](https://www.spiritswap.finance/)
- POLYGON:
	- [1] [QuickSwap](https://quickswap.exchange/)
- HECO:
	- [1] [MDEX (HECO)](https://ht.mdex.co/#/swap/)
- KCC:
	- [1] [KoffeeSwap](https://koffeeswap.exchange/)
- OKEX:
	- [1] [CherrySwap](https://www.cherryswap.net/)
	- [2] [JSwap](https://app.jswap.finance/)
	- [3] [PandaSwap](https://app.pandaex.org/)
- MOONRIVER:
	- [1] [Solarbeam](https://quickswap.exchange/)
- ARBITRUM:
	- [1] [SushiSwap](https://app.sushi.com/en/swap)
- BSC_TEST:
	- [1] [PancakeSwap v2 (TEST)]()

    
---


## Installation

* Download

```bash
pip install many-abis

# pypi
pip install -i https://pypi.org/simple many-abis

# update
pip install -U -i https://pypi.org/simple many-abis
```

## Usage

* Get dex and eth from default settings.

```python
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

```

* Print all supported chains and dexs.

```
ma.print_all_dex()

# output
----------------------
- BSC:
	- [1] [PancakeSwap v2](https://exchange.pancakeswap.finance/#/swap)
	- [2] [MDEX (BSC)](https://bsc.mdex.co/#/swap/)
	- [3] [ApeSwap Finance](https://app.apeswap.finance/swap)
	- [4] [BiSwap](https://exchange.biswap.org/#/swap)
	- [5] [Just Liquidity](https://dexbeta.julswap.com/)
- ETH:
	- [1] [Uniswap V2](https://app.uniswap.org/)
- AVAX:
	- [1] [traderjoexyz](https://traderjoexyz.com/#/home)
- FANTOM:
	- [1] [SpookySwap](https://spookyswap.finance/)
	- [2] [SpiritSwap](https://www.spiritswap.finance/)
- POLYGON:
	- [1] [QuickSwap](https://quickswap.exchange/)
- HECO:
	- [1] [MDEX (HECO)](https://ht.mdex.co/#/swap/)
- KCC:
	- [1] [KoffeeSwap](https://koffeeswap.exchange/)
- OKEX:
	- [1] [CherrySwap](https://www.cherryswap.net/)
	- [2] [JSwap](https://app.jswap.finance/)
	- [3] [PandaSwap](https://app.pandaex.org/)
- MOONRIVER:
	- [1] [Solarbeam](https://quickswap.exchange/)
- ARBITRUM:
	- [1] [SushiSwap](https://app.sushi.com/en/swap)
- BSC_TEST:
	- [1] [PancakeSwap v2 (TEST)]()
```

* If one DEX contract is not in the default settings, we can get abis from the contract address.

* you need to specify your `api_key` from the Block Explorer.

* KCC is not supported!

Here is an example to access open source dex abi from address.

```python
from many_abis.utils.utils import get_factory_from_router, get_abi_from_address
from many_abis.utils.enum.chain_rpc_enum import CHAIN_RPC_API as rpc
from many_abis.utils.enum.contract_api_enum import CHAIN_CONTRACT_API as contract_api

# get router abi
abi = get_abi_from_address('0x10ED43C718714eb63d5aA57B78B54704E256024E', 'YOUR_API_KEY', chain_api=contract_api.BSC)

# get factory abi
factory_address, factory_abi = get_factory_from_router('0x10ED43C718714eb63d5aA57B78B54704E256024E', 'YOUR_API_KEY',
                                                       chain_api=contract_api.BSC, rpc=rpc.BSC)

```
