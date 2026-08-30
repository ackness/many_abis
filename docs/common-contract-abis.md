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
| `OPENZEPPELIN_ACCESS_CONTROL_V5` | Role queries and administration | [`IAccessControl`, OpenZeppelin v5.6.1](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v5.6.1/contracts/access/IAccessControl.sol) |
| `OPENZEPPELIN_IERC1967` | Proxy upgrade/admin/beacon event decoding | [`IERC1967`, OpenZeppelin v5.6.1](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v5.6.1/contracts/interfaces/IERC1967.sol) |
| `CHAINLINK_AGGREGATOR_V3` | Price-feed reads | [`AggregatorV3Interface`, contracts-v1.5.0](https://github.com/smartcontractkit/chainlink-evm/blob/contracts-v1.5.0/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol) |
| `MULTICALL3` | Batched calls | [`Multicall3` v3.1.0 artifact](https://github.com/mds1/multicall3/releases/tag/v3.1.0) |
| `UNISWAP_PERMIT2` | Allowance and signature transfers | [`Permit2` deployment revision](https://github.com/Uniswap/permit2/tree/cc306b601f172c51bc04334a109e98340456620b) |

## Safety boundaries

- `ERC20_PERMIT` is the EIP-2612 shape. DAI-style permit uses different
  parameters and must not be decoded with this ABI.
- `ERC2981.royaltyInfo` reports royalty information; the standard does not
  enforce payment.
- `ERC4626` includes the inherited ERC-20 and metadata ABI. Preview values can
  change before execution and do not replace slippage limits.
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
