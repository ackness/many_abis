# Singleton DEX data and read-only examples

Uniswap v4 keeps pools in a single `PoolManager` per deployment. PancakeSwap
Infinity uses a shared accounting `Vault` with separate concentrated-liquidity
(CL) and liquidity-book (Bin) pool managers. Their pool keys, state layouts,
hooks, and swap commands are different. A currency pair alone does not identify
a pool: the complete key determines its ID. See the official
[Uniswap v4 pool types](https://github.com/Uniswap/v4-core/blob/main/src/types/PoolKey.sol)
and [PancakeSwap Infinity architecture](https://developer.pancakeswap.finance/contracts/infinity/overview).

`many_abis.get_contract("<chain>:dex:<protocol>:<role>")` supplies a registered
address and ABI name. The protocols used here are `uniswap-v4`,
`pancake-infinity-cl`, and `pancake-infinity-bin`; roles include `pool_manager`,
`quoter`, and `position_manager`. Uniswap v4 also has `state_view`, which reads
its manager's state. The example uses `deepcopy(ma.get_abi(record["abi"]))`
when constructing a `web3.py` contract. The registry contains deployment and
interface data; it does not discover routes or pool keys for a token pair.

## Pool keys and IDs

| Protocol | Ordered PoolKey fields | Read-only state source |
| --- | --- | --- |
| Uniswap v4 | `currency0`, `currency1`, `fee`, `tickSpacing`, `hooks` | `StateView.getSlot0(poolId)`, `getLiquidity(poolId)` |
| Infinity CL | `currency0`, `currency1`, `hooks`, `poolManager`, `fee`, `parameters` | `CLPoolManager.getSlot0(poolId)`, `getLiquidity(poolId)`, `poolIdToPoolKey(poolId)` |
| Infinity Bin | Same Infinity key shape, with Bin parameters and manager | `BinPoolManager.getSlot0(poolId)`, `getBin(poolId, activeId)`, `poolIdToPoolKey(poolId)` |

Addresses must be valid EVM addresses and `currency0` must sort below
`currency1` numerically. A static `fee` can be at most 1,000,000 in v4 or
Infinity CL and 100,000 in Infinity Bin; `0x800000` denotes a dynamic fee.
V4 `tickSpacing` must be 1–32767. Infinity `parameters` is a 32-byte hex
value whose packed meaning depends on CL or Bin. For Infinity, `poolManager` must be the registered manager
for the selected protocol and chain. A native currency uses the zero address
inside these keys; its wrapped token is a different currency with a different
address. Do not substitute WETH or WBNB for the zero address.
See the official [Infinity LP fee rules](https://github.com/pancakeswap/infinity-core/blob/main/src/libraries/LPFeeLibrary.sol).

The Uniswap v4 ID is exactly
`keccak256(abi.encode(PoolKey(currency0,currency1,fee,tickSpacing,hooks)))`,
using standard ABI encoding of the five-field struct, **not** packed encoding.
Infinity's six-field key has a different ID encoding. The example uses the
`web3.py` codec to ABI-encode the supplied key and computes its ID locally for
quotes. These definitions come from the official
[v4 `PoolIdLibrary`](https://github.com/Uniswap/v4-core/blob/main/src/types/PoolId.sol)
and [Infinity `PoolIdLibrary`](https://github.com/pancakeswap/infinity-core/blob/main/src/types/PoolId.sol).

## Run the example

Install the optional `web3.py` dependency and pass a trusted RPC through
`RPC_URL` or `--rpc-url`. `--help` needs neither a network connection nor
`web3.py`:

```bash
uv run python examples/singleton_pools.py --help
RPC_URL="https://your-provider.example" uv run --with web3 \
  python examples/singleton_pools.py state \
  --protocol uniswap-v4 --chain base --pool-id '0x<64 hex digits>'
RPC_URL="https://your-provider.example" uv run --with web3 \
  python examples/singleton_pools.py state \
  --protocol pancake-infinity-bin --chain bsc --pool-id '0x<64 hex digits>'
```

For a concrete read-only check, the Base ETH/USDC no-hook pool was verified
with fee `100` and tick spacing `1`. The default registered RPC is sufficient:

```bash
uv run --with web3==8.0.0 python examples/singleton_pools.py state \
  --protocol uniswap-v4 --chain base \
  --pool-id 0xe87077fd043c1a6afa5256104acb1d1eb5ca5bc031ee57f9d96c8172ead4bef8
```

Its PoolKey JSON is:

```json
{
  "currency0": "0x0000000000000000000000000000000000000000",
  "currency1": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
  "fee": 100,
  "tickSpacing": 1,
  "hooks": "0x0000000000000000000000000000000000000000"
}
```

Supply a real, complete PoolKey JSON object from an `Initialize` event or
another verified source. Field names and order are shown above; numeric
fields are JSON integers, and addresses and `parameters` are hex strings.
The quote command requires the full key, explicit direction, and exact input
amount in atomic currency units:

```bash
RPC_URL="https://your-provider.example" uv run --with web3 \
  python examples/singleton_pools.py quote \
  --protocol pancake-infinity-cl --chain bsc \
  --pool-key-file /path/to/pool-key.json \
  --zero-for-one --amount-in 1000000 --hook-data 0x
```

Use `--one-for-zero` for the reverse direction and `--from-address` when hooks
use the caller. Quoters expose `quoteExactInputSingle` with the protocol's
`PoolKey`, direction, `uint128 exactAmount`, and `hookData`. This method is
non-view in the ABI, but the example invokes only `eth_call`; it never sends a
transaction. It samples one block number and uses it for all reads in that
invocation, then prints the amount out and quoter gas estimate. Quotes are
simulations for that block and caller context. Hooks, pool state, fees, and
liquidity can change before execution. The relevant interfaces are
[Uniswap `IV4Quoter`](https://github.com/Uniswap/v4-periphery/blob/main/src/interfaces/IV4Quoter.sol)
and [Infinity `IQuoter`](https://github.com/pancakeswap/infinity-periphery/blob/main/src/interfaces/IQuoter.sol).

To decode a complete JSON log returned by an RPC receipt, pass its `address`,
`topics`, and `data` (and retain its receipt metadata):

```bash
uv run --with web3 python examples/singleton_pools.py decode-log \
  --protocol uniswap-v4 --chain base --log-file /path/to/log.json
```

Decoding is offline. The log address must match the selected protocol's
registered pool or position manager, and the event signature must occur in
that contract's ABI. Decoding bytes does not authenticate the receipt; check
its chain, transaction, block, and contract provenance separately.

The position manager and router ABIs include command bytes, but an ABI does
not construct those commands or validate a swap route. This phase provides
deployment lookup, direct state reads, one-pool quotes, and event decoding;
it does not encode position actions, route through pools, approve spending, or
submit swaps.

## Deployment versions and verification

Universal Router is registered independently as
`<chain>:dex:uniswap-universal-router-2-1-2:router`; Uniswap Permit2 is
`<chain>:dex:uniswap-permit2:permit2`. Infinity's shared router, vault and
Permit2 use `bsc:dex:pancake-infinity:<role>`. The two protocols use different
Permit2 addresses on BSC. Select a concrete deployment before constructing
any command bytes; an ABI alone does not specify those byte encodings.

See [verification evidence and test commands](singleton-verification.md) for
chain coverage, exact ABI sources, known interface differences, observed live
blocks, and initialized pool fixtures. `list_contracts(chain="bsc")` includes
all singleton components; the legacy `get_chain()["dex"]` shape remains
factory/router-only for compatibility.
