# Many Abis

![Version](https://img.shields.io/badge/many--abis-v0.2.0-green)
![Pypi](https://img.shields.io/pypi/dm/many-abis)

![GitHub Org's stars](https://img.shields.io/github/stars/ackness/many_abis?style=social)
![GitHub forks](https://img.shields.io/github/forks/ackness/many_abis?style=social)

---

Get different DEX abis easily for blockchain developers.

---

Now we support dex:

---

- arbitrum:
  - [1] [SushiSwap](https://app.sushi.com/en/swap)
  - [2] [Uniswap V3](https://app.uniswap.org/)
- avalanche:
  - [1] [LFJ Liquidity Book V2.2](https://lfj.gg/avalanche/trade)
- base:
  - [1] [Aerodrome Slipstream (Gauges V3)](https://aerodrome.finance/swap)
  - [2] [Uniswap V3](https://app.uniswap.org/)
  - [3] [PancakeSwap V3](https://pancakeswap.finance/swap)
- bsc:
  - [1] [PancakeSwap v2](https://pancakeswap.finance/swap)
  - [2] [PancakeSwap v3](https://pancakeswap.finance/swap)
  - [3] [Uniswap V3](https://app.uniswap.org/)
- bsc-test:
  - [1] [PancakeSwap v2 (TEST)]()
  - [2] [PancakeSwap v3 (TEST)](https://pancakeswap.finance/swap?chain=bscTestnet)
- cronos:
  - [1] [VVS Finance V2](https://vvs.finance/swap)
- eth:
  - [1] [Uniswap V2](https://app.uniswap.org/)
  - [2] [Uniswap V3](https://app.uniswap.org/)
- monad:
  - [1] [Uniswap V3](https://app.uniswap.org/)
- polygon:
  - [1] [QuickSwap](https://quickswap.exchange/)
  - [2] [Uniswap V3](https://app.uniswap.org/)
- optimism:
  - [1] [Uniswap V3](https://app.uniswap.org/#/swap)
  - [2] [Velodrome Slipstream](https://velodrome.finance/swap)
- robinhood:
  - [1] [Uniswap V3](https://app.uniswap.org/)
- sonic:
  - [1] [Shadow Exchange CLMM](https://www.shadow.so/)
- unichain:
  - [1] [Uniswap V3](https://app.uniswap.org/)
- xlayer:
  - [1] [Uniswap V3](https://app.uniswap.org/)

---

Chain, token, RPC, and DEX contract entries follow the documented
[source and verification policy](https://github.com/ackness/many_abis/blob/main/docs/chain-data-sources.md). DEX volume is used
to prioritize candidates, while official deployment documentation and on-chain
bytecode are required before an address is added. These checks do not replace a
smart-contract security audit.

---

## Installation

- Download

```bash
pip install many-abis

# pypi
pip install -i https://pypi.org/simple many-abis

# update
pip install -U many-abis
# or
pip install -U -i https://pypi.org/simple many-abis
```

## Usage

```python
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
    "0x10ED43C718714eb63d5aA57B78B54704E256024E",
    "YOUR API KEY",
    ma.CHAIN_CONTRACT_API.BSC
)

# ======================================================================
# chains
chains = ma.all_chains()
print(chains)
# ['arbitrum', 'avalanche', 'base', 'bsc', 'bsc-test', 'cronos', 'eth',
#  'hyperevm', 'monad', 'optimism', 'polygon', 'robinhood', 'sonic',
#  'unichain', 'xlayer']

# different methods to get chain
bsc = ma.get_chain_by_id(chain_id=56)
bsc = ma.get_chain_by_name(name="bsc")
bsc = ma.get_chain(name="bsc")
bsc = ma.get_chain(chain_id=56)
bsc = ma.chain(name="bsc")
bsc = ma.chain(chain_id=56)
print(bsc)

# use ['key'] or dot key name to access chain info
print(bsc['chain_id'])
# 56
print(bsc.name)
# Binance Smart Chain Mainnet
print(bsc.dex.pancake_v2.router_address)
# 0x10ED43C718714eb63d5aA57B78B54704E256024E

# to get some items from chain
eth_weth = ma.get('eth', 'weth')
print(eth_weth)
# {'address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'name': 'Wrapped ETH', 'symbol': 'WETH'}

ds = ma.get('bsc', 'dex', 'pancake_v2')
print(ds)
# {'factory_address': '0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73', 'name': 'PancakeSwap v2', 'router_address': '0x10ED43C718714eb63d5aA57B78B54704E256024E', 'website': 'https://pancakeswap.finance/swap'}

# print all dex
ma.print_all_dex()

```
