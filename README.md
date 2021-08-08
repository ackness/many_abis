# Many Abis [v0.0.11]

Get different DEX abis easily for block chain developers.

---

Now we support: 

---

- BSC:
  - DEX:
    - [0] [BakerySwap](https://www.bakeryswap.org/)
    - [1] [Just Liquidity](https://dexbeta.julswap.com/)
    - [2] [MDEX (BSC)](https://bsc.mdex.co/#/swap/)
    - [3] [PancakeSwap v1](https://v1exchange.pancakeswap.finance/#/)
    - [4] [PancakeSwap v2](https://exchange.pancakeswap.finance/#/swap)
    - [5] [ApeSwap Finance](https://app.apeswap.finance/swap)
- ETH:
  - DEX:
    - [0] [Uniswap V2](https://app.uniswap.org/)
- HECO:
  - DEX:
    - [0] [MDEX (HECO)](https://ht.mdex.co/#/swap/)
- MATIC:
  - DEX:
    - [0] [QuickSwap](https://quickswap.exchange/)
- KCC:
  - DEX:
    - [0] [KoffeeSwap](https://koffeeswap.exchange/)
- OKEX:
  - DEX:
    - [0] [PandaSwap](https://app.pandaex.org/)
    - [1] [CherrySwap](https://www.cherryswap.net/)
    - [2] [JSwap](https://app.jswap.finance/)
- BSC_TEST:
  - DEX:
    - [0] [PancakeSwap v2 (TEST)]()
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
from web3 import Web3
from many_abis import get, print_all_support
from many_abis.utils.chain_rpc_enum import CHAIN_RPC_API as rpc

# get dex and chain info 
chain_info, dex_info = get(chain='BSC', dex='pancake_v2')
print(chain_info.keys())
print(dex_info.keys())

# and we can use web3 to get dex contract
web3 = Web3(Web3.HTTPProvider(rpc.BSC))
contract = web3.eth.contract(address=dex_info['router_address'], abi=dex_info['router_abi'])
print(contract.all_functions())

# output
----------------------

# chain info
dict_keys(['chain', 'explorer', 'weth', 'coins', 'charts', 'rpc'])
----------------------
# dex info
dict_keys(['name', 'router_address', 'router_abi', 'factory_address', 'factory_abi', 'website'])
----------------------
# contract
[<Function WETH()>, ...]
----------------------
```

* Print all supported chains and dexs.

```
print_all_support()

# output
----------------------
- BSC:
  - DEX:
    - [0] [BakerySwap](https://www.bakeryswap.org/)
    - [1] [Just Liquidity](https://dexbeta.julswap.com/)
    - [2] [MDEX (BSC)](https://bsc.mdex.co/#/swap/)
    - [3] [PancakeSwap v1](https://v1exchange.pancakeswap.finance/#/)
    - [4] [PancakeSwap v2](https://exchange.pancakeswap.finance/#/swap)
    - [5] [ApeSwap Finance](https://app.apeswap.finance/swap)
- ETH:
  - DEX:
    - [0] [Uniswap V2](https://app.uniswap.org/)
- HECO:
  - DEX:
    - [0] [MDEX (HECO)](https://ht.mdex.co/#/swap/)
- MATIC:
  - DEX:
    - [0] [QuickSwap](https://quickswap.exchange/)
- KCC:
  - DEX:
    - [0] [KoffeeSwap](https://koffeeswap.exchange/)
- OKEX:
  - DEX:
    - [0] [PandaSwap](https://app.pandaex.org/)
    - [1] [CherrySwap](https://www.cherryswap.net/)
    - [2] [JSwap](https://app.jswap.finance/)
- BSC_TEST:
  - DEX:
    - [0] [PancakeSwap v2 (TEST)]()
----------------------
```

* If one DEX contract is not in the default settings, we can get abis from the contract address.

* you need to specify your `api_key` from the Block Explorer.

* KCC is not supported!

```python
from many_abis.utils import get_abi_from_address, get_factory_from_router
from many_abis.utils.chain_rpc_enum import CHAIN_RPC_API as rpc
from many_abis.utils.contract_api_enum import CHAIN_CONTRACT_API as contract_api

# get router abi
abi = get_abi_from_address('0x10ED43C718714eb63d5aA57B78B54704E256024E', 'YOUR_API_KEY', chain_api=contract_api.BSC))

# get factory abi
factory_address, factory_abi = get_factory_from_router('0x10ED43C718714eb63d5aA57B78B54704E256024E', 'YOUR_API_KEY', chain_api=contract_api.BSC, rpc=rpc.BSC)

```
