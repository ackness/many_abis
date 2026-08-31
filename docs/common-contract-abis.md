# Common contract ABIs

These ABIs are intended for reusable EVM development tasks. They are copied
from fixed official artifacts or reproduced from a fixed source revision; they
are not handwritten subsets. An ABI proves only the encoded interface shape.
It does not prove that an address implements the interface correctly, that a
deployment is official, or that a returned value is safe to use.

| ABI | Typical use | Fixed source |
| --- | --- | --- |
| `ERC165` | Interface detection | [`IERC165`, OpenZeppelin v5.6.1](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v5.6.1/contracts/utils/introspection/IERC165.sol) |
| `ERC1271` | Smart-contract signature validation | [`IERC1271`, OpenZeppelin v5.6.1](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v5.6.1/contracts/interfaces/IERC1271.sol) |
| `ERC20_PERMIT` | EIP-2612 approvals by signature | [`IERC20Permit`, OpenZeppelin v5.6.1](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v5.6.1/contracts/token/ERC20/extensions/IERC20Permit.sol) |
| `ERC2981` | NFT royalty information | [`IERC2981`, OpenZeppelin v5.6.1](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v5.6.1/contracts/interfaces/IERC2981.sol) |
| `ERC4626` | Tokenized vault interactions | [`IERC4626`, OpenZeppelin v5.6.1](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v5.6.1/contracts/interfaces/IERC4626.sol) |
| `ERC5267` | EIP-712 domain introspection | [`IERC5267`, OpenZeppelin v5.6.1](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v5.6.1/contracts/interfaces/IERC5267.sol) |
| `ERC6093_ERC20_ERRORS` | Decode standard ERC-20 custom errors | [`IERC20Errors`, OpenZeppelin v5.6.1](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v5.6.1/contracts/interfaces/draft-IERC6093.sol) |
| `ERC6093_ERC721_ERRORS` | Decode standard ERC-721 custom errors | [`IERC721Errors`, OpenZeppelin v5.6.1](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v5.6.1/contracts/interfaces/draft-IERC6093.sol) |
| `ERC6093_ERC1155_ERRORS` | Decode standard ERC-1155 custom errors | [`IERC1155Errors`, OpenZeppelin v5.6.1](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v5.6.1/contracts/interfaces/draft-IERC6093.sol) |
| `ERC6909` | Minimal multi-token transfers and approvals | [`IERC6909`, OpenZeppelin v5.6.1](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v5.6.1/contracts/interfaces/IERC6909.sol) |
| `ERC6909_METADATA` | Expanded ERC-6909 interface with per-ID metadata | [`IERC6909Metadata`, OpenZeppelin v5.6.1](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v5.6.1/contracts/interfaces/IERC6909.sol) |
| `OPENZEPPELIN_ACCESS_CONTROL_V5` | Role queries and administration | [`IAccessControl`, OpenZeppelin v5.6.1](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v5.6.1/contracts/access/IAccessControl.sol) |
| `OPENZEPPELIN_IERC1967` | Proxy upgrade/admin/beacon event decoding | [`IERC1967`, OpenZeppelin v5.6.1](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v5.6.1/contracts/interfaces/IERC1967.sol) |
| `CHAINLINK_AGGREGATOR_V3` | Price-feed reads | [`AggregatorV3Interface`, contracts-v1.5.0](https://github.com/smartcontractkit/chainlink-evm/blob/contracts-v1.5.0/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol) |
| `MULTICALL3` | Batched calls | [`Multicall3` v3.1.0 artifact](https://github.com/mds1/multicall3/releases/tag/v3.1.0) |
| `UNISWAP_PERMIT2` | Allowance and signature transfers | [`Permit2` deployment revision](https://github.com/Uniswap/permit2/tree/cc306b601f172c51bc04334a109e98340456620b) |
| `UNISWAP_V3_POOL_STATE` | Read Uniswap V3 pool state without write methods | [`IUniswapV3PoolState`, v3-core 1.0.1](https://github.com/Uniswap/v3-core/blob/ed88be38ab2032d82bf10ac6f8d03aa631889d48/contracts/interfaces/pool/IUniswapV3PoolState.sol) |
| `UNISWAP_V3_POOL_EVENTS` | Decode the nine Uniswap V3 core pool events | [`IUniswapV3PoolEvents`, v3-core 1.0.1](https://github.com/Uniswap/v3-core/blob/ed88be38ab2032d82bf10ac6f8d03aa631889d48/contracts/interfaces/pool/IUniswapV3PoolEvents.sol) |

## Safety boundaries

- `ERC20_PERMIT` is the EIP-2612 shape. DAI-style permit uses different
  parameters and must not be decoded with this ABI.
- `ERC2981.royaltyInfo` reports royalty information; the standard does not
  enforce payment.
- `ERC4626` includes the inherited ERC-20 and metadata ABI. Preview values can
  change before execution and do not replace slippage limits.
- `ERC5267` values help construct and inspect an EIP-712 domain, but a returned
  domain does not authenticate the target contract. Validate the field bitmap,
  `chainId`, and `verifyingContract` against the intended signature flow.
- ERC-6093 revert data can be forged by any contract. Error decoding explains
  bytes; it does not prove that the reverting address implements an ERC.
- `ERC6909.setOperator` grants authority across every token ID owned by the
  caller. `ERC6909_METADATA` is the complete inherited interface, not a
  metadata-only read subset.
- `OPENZEPPELIN_ACCESS_CONTROL_V5` includes OpenZeppelin v5 custom errors. Do
  not assume every role-based contract uses this exact implementation version.
- `OPENZEPPELIN_IERC1967` contains events only. Read current implementation,
  admin, and beacon values from the EIP-1967 storage slots; events are not
  authoritative current state.
- For Chainlink feeds, verify each address through official chain-specific feed
  documentation and validate `updatedAt`, freshness, decimals, and application
  bounds. The interface alone does not authenticate a feed. The recorded MIT
  evidence applies to this interface source file; it is not a claim that the
  entire `@chainlink/contracts` package is MIT-licensed.
- Multicall3 is not guaranteed to exist on every chain. Verify deployed
  bytecode before using a presumed canonical address, and treat
  `aggregate3Value` as a value-moving call rather than a read helper. The
  upstream project also states that transaction use has not been audited.
- Permit2 creates powerful token permissions. Verify the exact chain
  deployment and bytecode, bind signatures to the intended spender, amount,
  nonce, deadline, and witness, and never infer deployment from its canonical
  address alone.
- Uniswap V3 pool state is manipulable within a transaction and must not be
  treated as an authenticated or manipulation-resistant price. Authenticate a
  pool through the intended factory and deployment evidence.

High-risk proxy administration ABIs are deliberately omitted. OpenZeppelin 4.x
and 5.x proxy-admin interfaces differ, transparent proxy dispatch depends on
the caller, and UUPS functions must be called against the correct proxy or
implementation context.

## Reproducing the artifacts

The exact package integrity values and artifact paths are stored in
`registry/abi-metadata.json` and copied into the generated ABI index.
OpenZeppelin ABIs come from `package/build/contracts/*.json#abi` in
`@openzeppelin/contracts@5.6.1`. The Chainlink ABI comes from
`package/abi/v0.8/shared/AggregatorV3Interface.abi.json` in
`@chainlink/contracts@1.5.0`. Multicall3 uses the `.abi` field of the official
v3.1.0 release artifact.

The two Uniswap V3 pool subsets come from the fixed
`@uniswap/v3-core@1.0.1` npm artifacts. Their interface sources carry the more
specific `GPL-2.0-or-later` terms recorded in the generated provenance and
third-party notices.

Aave V3 `IPoolDataProvider` is deliberately omitted. The historical
[`@aave/core-v3@1.19.3`](https://github.com/aave/aave-v3-core/releases/tag/v1.19.3)
interface has already diverged from current
[`aave-v3-origin`](https://github.com/aave-dao/aave-v3-origin/releases/tag/v3.6.0)
deployments; a future addition must bind an immutable
[Address Book release](https://github.com/aave-dao/aave-address-book/releases),
interface revision, and verified per-chain Data Provider address.

Permit2 has no official npm contract artifact. It is reproduced from the fixed
deployment revision and its committed submodule revisions:

```bash
git clone --depth 1 \
  --branch 0x000000000022D473030F116dDEE9F6B43aC78BA3 \
  https://github.com/Uniswap/permit2.git
cd permit2
git submodule update --init
forge build src/Permit2.sol --skip test --skip script --force
jq '.abi' out/Permit2.sol/Permit2.json
```

That revision pins Solidity 0.8.17. The generated ABI must retain canonical
SHA-256 `28c807df09f0d09db5a55b95280d544ca01952232e393f76f00ccb4b37cc3ef0`.
