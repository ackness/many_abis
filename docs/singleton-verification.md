# Singleton deployment verification

Reviewed 2026-09-29. This change adds 13 ABI resources and 81 logical
contract deployments: six Uniswap components on each of 12 mainnet chains,
and nine BSC PancakeSwap Infinity components. The original 99 address snapshots
are unchanged. Each new address has a registered-RPC chain-ID check, nonempty
runtime code, a code hash, EIP-1967 observations, and a pinned block in
`registry/verification-snapshots.json`.

## ABI and deployment provenance

Uniswap addresses were checked against the official
[deployment feed](https://developers.uniswap.org/deployments.json), generated
2026-09-22 from [Uniswap/contracts at a677c0d4](https://github.com/Uniswap/contracts/tree/a677c0d4b5fb6e3357cf6d0f0315bcb135a1e1ee).
The feed's short `sourceRef` hashes can identify deployment-repository commits;
they are not necessarily v4-core/periphery source commits. The immutable ABI
source and the reviewed deployment revision are recorded separately.

- `UNISWAP_V4_POOL_MANAGER` is compiled from the MIT `IPoolManager` interface
  in `@uniswap/v4-core@1.0.0`, not the BUSL implementation. It deliberately
  omits implementation-only constructor, Ownable and ERC165 entries.
- StateView, Quoter and PositionManager are compiled from MIT sources in
  `@uniswap/v4-periphery@1.0.0`. The shared interfaces cover the common calls.
  Some newer deployments add methods/events: HyperEVM and Robinhood Quoters
  add `msgSender()`, and HyperEVM PositionManager adds `ModifyPosition`.
  These additions are not exposed by this common ABI. StateView's source ABI
  also includes a `NotPoolManager` error absent from the compared deployment.
- Universal Router `2.1.2` uses the Sourcify-verified deployed Ethereum ABI;
  its canonical ABI hash matched all 12 registered chains. The npm `2.1.0`
  compiled artifact had ten differing error signatures despite identical
  top-level source files, so it was not used. Its license is GPL-3.0-or-later.
- Infinity's eight implementation ABIs come from the Sourcify-verified BSC
  deployments, with metadata hashes pinned in `registry/abi-metadata.json`.
  Their verified concrete source files specify GPL-2.0-or-later. Addresses
  agree with the pinned official [core config](https://github.com/pancakeswap/infinity-core/blob/d0e879334da8ea789a895d864dbe34259ea9fb65/script/config/bsc-mainnet.json),
  [periphery config](https://github.com/pancakeswap/infinity-periphery/blob/4efea658a051305052a948c74632c01470e769e2/script/config/bsc-mainnet.json),
  and [router deployment](https://github.com/pancakeswap/infinity-universal-router/blob/923a357fa07e9b527d5aefeec724c1bb12189da0/deploy-addresses/bsc-mainnet.json).
- PancakeSwap Permit2 is `0x31c2F6fcFf4F8759b3Bd5Bf0e1084A055615c768`, not
  Uniswap's canonical address. Its deployed ABI has the same 31 callable,
  event and error signatures as the existing bundled Permit2 ABI.

Sourcify returned verified artifacts for 56 of the 72 Uniswap deployments;
all required signatures occurred in those artifacts. The other 16 have
independent official deployment records and successful live code/getter
checks, but no Sourcify artifact comparison was available during this review.
An official address, ABI source provenance and successful calls are separate
kinds of evidence; this review is not complete byte-for-byte source
recompilation for every deployment or a smart-contract security audit.

## Live read checks

All 81 new deployments passed runtime code-hash checks. The tests additionally
performed 186 `eth_call` operations, checking manager, vault, position-manager
and Permit2 relationships; position metadata; Permit2 allowances/nonces; and
pool state and quotes. Calls on each chain use one numbered block and the
block hash is checked again afterward. No approval, signing, or transaction
broadcast was performed.

| Chain | Live-call block | Successful calls | Uniswap Sourcify artifacts |
| --- | ---: | ---: | ---: |
| `arbitrum` | 510062316 | 12 | 6/6 |
| `avalanche` | 96396791 | 12 | 3/6 |
| `base` | 51952445 | 15 | 6/6 |
| `bsc` | 124737317 | 51 | 6/6 |
| `eth` | 26083871 | 12 | 6/6 |
| `hyperevm` | 47211331 | 12 | 5/6 |
| `monad` | 109065933 | 12 | 2/6 |
| `optimism` | 157547565 | 12 | 6/6 |
| `polygon` | 94659274 | 12 | 6/6 |
| `robinhood` | 75745930 | 12 | 6/6 |
| `unichain` | 59945556 | 12 | 3/6 |
| `xlayer` | 71924888 | 12 | 1/6 |

The initialized no-hook fixtures in `tests/fixtures/singleton-pools.json` are:

| Protocol | Chain | Currencies | Read calls |
| --- | --- | --- | --- |
| Uniswap v4 | Base | native ETH / USDC | `getSlot0`, `getLiquidity`, `quoteExactInputSingle` |
| Infinity CL | BSC | Binance-peg USDT / USDC | `getSlot0`, `getLiquidity`, `poolIdToPoolKey`, `quoteExactInputSingle` |
| Infinity Bin | BSC | Binance-peg USDT / USDC | `getSlot0`, `getBin`, `poolIdToPoolKey`, `quoteExactInputSingle` |

The live tests recompute pool IDs, require initialized state and nonzero
liquidity/reserves, verify stored Infinity keys, and require positive quote
outputs and gas estimates. They do not pin exchange rates or assume liquidity
will remain available. Real Swap logs from these three pools are retained in
`tests/fixtures/singleton-swap-logs.json` for offline ABI decoding regression
checks. They are public on-chain logs, not user wallet exports.

## Reproduce checks

```bash
uv run --frozen python scripts/generate_registry.py --check
uv run --frozen python -m unittest discover -s tests -v
uv run --frozen --with web3==8.0.0 python -m unittest discover -s tests -p test_singleton_examples.py -v
MANY_ABIS_LIVE_TESTS=1 uv run --frozen --with web3==8.0.0 python -m unittest discover -s tests -p test_singleton_live.py -v
```

`MANY_ABIS_LIVE_CHAIN=bsc` limits live checks to one chain. Live checks are
opt-in because public RPC availability, pool liquidity and chain state change.
Ordinary CI runs the offline suite and the optional web3 example tests. The
web3 dependency stays optional for package consumers. Old block replay may
require an archive RPC.

To reproduce the source-derived v4 ABIs, unpack the exact npm tarballs linked
in `registry/abi-metadata.json` (verify their recorded SHA-512 integrity), then
run `forge inspect <source>:<contract> abi --root <unpacked-package> --json`
with solc 0.8.26. The four targets are `src/interfaces/IPoolManager.sol:IPoolManager`,
`src/lens/StateView.sol:StateView`, `src/lens/V4Quoter.sol:V4Quoter`, and
`src/PositionManager.sol:PositionManager`. For the deployed ABI resources,
retrieve the recorded Sourcify response and extract its `abi` array; check the
canonical SHA-256 before accepting a refresh. Source URLs require manual
review; the offline generator cannot authenticate an arbitrary HTTPS source.
