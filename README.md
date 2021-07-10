# Many Abis

Get different DEXs abis easily for block chain developer.

## Installation

* Download with pypi

```bash
pip install many_abis
```

## Usage

* Get dex and eth from default settings.

```python
from web3 import Web3
from many_abis import get, print_all_support
from many_abis.chain_rpc_enum import CHAIN_RPC_API as rpc

# get dex and eth 
dex, weth = get(chain='BSC', dex='pancake_v2')
print(dex.keys())
print(weth.keys())

# and we can use web3 to get dex contract
web3 = Web3(Web3.HTTPProvider(rpc.BSC))
contract = web3.eth.contract(address=dex['router_address'], abi=dex['router_abi'])
print(contract.all_functions())

# output
----------------------
# dex
dict_keys(['name', 'router_address', 'router_abi', 'factory_address', 'factory_abi'])
----------------------
# weth
dict_keys(['name', 'symbol', 'address', 'abi'])
----------------------
# contract
[<Function WETH()>, ...]
----------------------
```

* Print all supported chains and dexs.

```python
print_all_support()

# output
----------------------
Chain-0: BSC
        DEX-0: bakery
        DEX-1: jul
        DEX-2: mdex_bsc
        DEX-3: pancake_v1
        DEX-4: pancake_v2
Chain-1: ETH
        DEX-0: uniswap_v2
Chain-2: HECO
        DEX-0: mdex_heco
Chain-3: MATIC
        DEX-0: quickswap
----------------------
```

* If contract not in the default settings, we can get abis from address.

* you need to specify your `api_key` from the Block Explorer.

```python
from many_abis.utils import get_abi_from_address, get_factory_from_router
from many_abis.utils.chain_rpc_enum import CHAIN_RPC_API as rpc
from many_abis.utils.contract_api_enum import CHAIN_CONTRACT_API as contract_api

# get router abi
abi = get_abi_from_address('0x10ED43C718714eb63d5aA57B78B54704E256024E', 'YOUR_API_KEY', chain_api=contract_api.BSC))

# get factory abi
factory_address, factory_abi = get_factory_from_router('0x10ED43C718714eb63d5aA57B78B54704E256024E', 'YOUR_API_KEY', chain_api=contract_api.BSC, rpc=rpc.BSC)

```
