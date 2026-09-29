# Registry verification and query API

The v0.4 registry adds evidence without changing the legacy `chains.json`
shape. Existing `chain()`, `get_chain()`, and `get()` callers continue to see
the same chain objects.

## Generated data layers

| Packaged file | Purpose | Source |
| --- | --- | --- |
| `assets/contract-index.json` | Logical protocol components and token records | `registry/chains/*.json`, `registry/deployments/*.json`, and token policy overrides |
| `assets/token-index.json` | Configured and on-chain symbols, decimals, and conservative origin labels | Chain sources, token policies, and snapshots |
| `assets/verification-snapshots.json` | Block-pinned runtime code and EIP-1967 observations | `registry/verification-snapshots.json` |

The contract index identifies a logical role such as
`base:dex:uniswap-v3:router`. Verification records instead use
`chain:lowercase-address`, because one address can serve more than one logical
role and the same address can contain different code on different chains.
Explicit deployments add roles such as `pool_manager`, `state_view`, `quoter`,
`position_manager`, `vault`, and `permit2`, without inventing factories for
singleton protocols. They use IDs such as `base:dex:uniswap-v4:state_view`.
`deployment_version` records the reviewed deployment release or revision;
the referenced ABI has its own immutable source in `get_abi_info()`.
`source_reviewed_at` is the review date of the chain or deployment source; it is not a
claim that the contract passed a security review.

## Snapshot semantics

Each verification record stores:

- the chain ID, RPC URL, block number, block hash, tag, and observation time;
- runtime bytecode size and Keccak-256 hash;
- EIP-1967 implementation, admin, and beacon storage-slot observations;
- implementation code hash when the standard implementation slot is populated;
- `symbol()` and `decimals()` results for configured tokens.

The snapshot proves what the selected RPC returned at one named block. It does
not prove that the contract is safe, that a source is verified, or that a proxy
will not upgrade later. Empty EIP-1967 slots mean only that this standard proxy
pattern was not observed; custom proxies, diamonds, minimal proxies, and
metamorphic designs require separate analysis.

The refresher rereads the numbered block after all state queries and aborts if
its hash changed, preventing a snapshot from mixing pre- and post-reorg state.
`latest` snapshots are anchored by block hash but may still be reorganized
after collection.
Use `--block-tag safe` or `--block-tag finalized` only on chains whose reviewed
RPC supports that tag, and inspect the resulting diff.

## Public query API

All returned objects are defensive plain-dictionary copies:

```python
import many_abis as ma

abi_info = ma.get_abi_info("ERC5267")
signature_abis = ma.find_abis(contract_role="signature")

router = ma.get_contract("base:dex:uniswap-v3:router")
base_contracts = ma.list_contracts(chain="base")

usdc = ma.get_token("base", "USDC")
bridged_tokens = ma.list_tokens(origin="bridged")

snapshot = ma.get_verification("base", usdc["address"])
same_snapshot = ma.get_verification(8453, usdc["address"])
```

Token origin is deliberately not inferred as native merely because the symbol
looks familiar. `unknown` means no origin claim is recorded. `issuer_native`,
`protocol_native`, and `bridged` require an explicit policy with evidence;
qualified configured symbols such as `USDT0` or `USDG.oft` are not sufficient.

## Refresh workflow

The offline generator never contacts a network. Snapshot refresh is a separate,
explicit command that uses only RPC URLs already admitted to the chain registry:

```bash
uv run python scripts/refresh_verifications.py --chain base --write
uv run python scripts/generate_registry.py --write
uv run python scripts/generate_registry.py --check
uv run python -m unittest discover -s tests -v
```

When adding deployments, `--missing-only` collects evidence for new addresses
and preserves existing snapshots. The generator rejects duplicate logical
deployments, unknown chains, mismatched ABI roles, and missing or extraneous
address snapshots. New protocol interfaces also need reviewed bindings in
`DEPLOYMENT_ABIS` in the generator; this prevents mixing CL/Bin managers or
StateView/Quoter ABIs with the same broad ABI role. Full refreshes also include
explicit deployments.

See [singleton DEX usage](singleton-dexes.md) for Uniswap v4 and PancakeSwap
Infinity read-only examples and version boundaries.

The refresh aborts before writing when a chain ID is wrong, a registered address
has no runtime bytecode, a Token metadata call is unusable, or an EIP-1967
implementation has no code. A successful refresh still requires human review of
address, code-hash, proxy, token, source, and policy changes before commit.

Scheduled automation may generate a report or draft pull request in the future;
it must not automatically merge address or implementation changes.
