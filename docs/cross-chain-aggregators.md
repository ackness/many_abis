# Cross-chain aggregators and settlement contracts

This registry treats API-driven aggregators differently from AMMs. An aggregator
API may select a solver, DEX, intermediate token, bridge, destination call, and
execution contract at quote time. A static ABI can decode calldata, but cannot
reproduce the route or prove that a quote is authentic and safe to execute.

An aggregator contract is added only when all of the following are available:

- an immutable official ABI and redistribution license;
- a stable, chain-specific deployment map from an official source;
- verified deployed bytecode, including the implementation and administrator
  when a proxy is used;
- audit evidence that covers the deployed revision and the security-critical
  offchain components on which settlement depends;
- documented trust, upgrade, refund, and emergency-control boundaries.

Passing the ABI and bytecode checks establishes contract identity. It does not
by itself establish protocol safety.

## Relay

**Decision as of 2026-08-31: deferred; no Relay ABI or address is included.**

Relay is a cross-chain payments and execution aggregator, not an AMM. Its API
quotes same-chain and cross-chain swaps, bridges, and calls. A cross-chain
request generally follows this flow:

1. The API returns transaction and signature steps.
2. The origin transaction deposits funds into `RelayDepository` with an order
   ID.
3. A solver uses its own inventory to complete the destination action.
4. Relay's Oracle attests the deposit and fill, and the Hub records settlement.
5. An allocator-authorized call releases funds from the origin Depository.

See Relay's [execution overview](https://docs.relay.link/how-relay-works),
[protocol overview](https://docs.relay.link/references/protocol/overview), and
[EVM Depository reference](https://docs.relay.link/references/protocol/contracts/evm-depository).
Applications need Relay's API or RelayKit to obtain a current route; an ABI is
not a substitute for that integration.

### What was verified

The official 33-item `RelayDepository` ABI at
[`relay-settlement@794dd7b`](https://github.com/relayprotocol/relay-settlement/blob/794dd7b3d3dda1dc80b7aa6b0903ec3ec0bb953b/packages/abis/src/abis/depository/RelayDepository.sol/RelayDepository.json)
has canonical SHA-256
`accf00a260b9fdf1e263ee733ac36b9e4c8333f5871c936430a8db229a8615d6`.
This identifies the reviewed artifact but is intentionally not copied into this
package.

Relay's live [`/chains` API](https://api.relay.link/chains) and
[Settlement address page](https://docs.relay.link/references/protocol/addresses)
reported the same Depository on Ethereum, Optimism, Base, and Arbitrum:
`0x4cD00E387622C35bDDB9b4c962C136462338BC31`.

The deployment source at
[`relay-depository@490858d`](https://github.com/relayprotocol/relay-depository/tree/490858d742d1083bc4e3c2884798f6491dc72abb/packages/ethereum-vm)
was rebuilt with Solidity 0.8.28, Cancun EVM, and `via_ir = true`. Runtime code
from all four chains matched the build after normalizing the five EIP-712
immutable slots. [Sourcify's Base record](https://sourcify.dev/server/v2/contract/8453/0x4cd00e387622c35bddb9b4c962c136462338bc31?fields=abi,metadata,sources)
independently reports an exact source match. The contract is a direct,
non-proxy deployment.

These checks establish the ABI, source, address, and bytecode relationship.
They are not the reason for deferral.

### Why it is deferred

- `RelayDepository` has no user-controlled timeout or unilateral refund path.
  Releasing deposited funds depends on an allocator authorization.
- `owner` can replace `allocator`; a valid allocator signature authorizes the
  arbitrary calls contained in `execute(CallRequest,bytes)`. `setAllocator`
  emits no allocator-change event.
- During the 2026-08-31 snapshot, all four chains returned
  `owner = 0xF61A305199fa1135d76FFaB3752D42F55cBd775A` and
  `allocator = 0x63C1d3E9C646184529C5694630a01C00dF171b56`. Both
  addresses had empty bytecode on those chains. Any external MPC or custody
  policy is not enforced or visible in the source-chain contract.
- The November 2025
  [Zellic Settlement assessment](https://raw.githubusercontent.com/relayprotocol/relay-settlement/794dd7b3d3dda1dc80b7aa6b0903ec3ec0bb953b/docs/audits/Zellic-Relay-Settlement.pdf)
  covered the EVM Depository revision and reported 11 findings, with an impact
  breakdown of 1 Critical, 2 High, 5 Medium, 2 Low, and 1 Informational. Its
  assessment conclusion did not consider the reviewed system production-ready
  and recommended another comprehensive assessment including the Hub and
  offchain Oracle.
- Settlement finding 3.10 remains acknowledged rather than removed: the
  three-argument `depositErc20(address,address,bytes32)` consumes the caller's
  full current allowance, which can permit block-ordering to reassign deposit
  credit. The explicit-amount overload or an atomic approve/deposit flow avoids
  that specific issue.
- The April 2026
  [Zellic Oracle assessment](https://raw.githubusercontent.com/relayprotocol/relay-settlement/794dd7b3d3dda1dc80b7aa6b0903ec3ec0bb953b/docs/audits/Zellic-Relay-Protocol-Oracle.pdf)
  reported 10 findings, with an impact breakdown of 2 Critical, 3 High,
  3 Medium, 1 Low, and 1 indeterminate. It records remediation for several
  findings but still recommends a comprehensive reassessment. No public
  follow-up report closing that recommendation was found in the
  [official audit index](https://github.com/relayprotocol/relay-settlement/blob/794dd7b3d3dda1dc80b7aa6b0903ec3ec0bb953b/docs/audits/README.md).
- The Certora report in the same index covers Solana programs, so it is not
  independent evidence for the EVM Depository.
- Relay's public API currently exposes one periphery deployment set, while the
  official
  [`relay-periphery@0a94c85`](https://github.com/relayprotocol/relay-periphery/tree/0a94c85932ada7f2c9bd8dc306948394c6cadbee)
  repository documents newer v3.1 Router and ApprovalProxy addresses. A static
  Router, Receiver, or ApprovalProxy entry would therefore risk mixing
  deployment generations.

The protocol may have operational controls that are stronger than what is
visible publicly. Under this registry's conservative policy, unobservable
controls and audit remediation claims are not treated as verified guarantees.

### Conditions for reconsideration

Relay can be reviewed again when the following evidence is public:

- a follow-up assessment covering the remediated Depository, Hub, Oracle,
  allocator, and production deployment revisions;
- a stable, versioned periphery address manifest reconciled with the live API;
- a documented and independently verifiable allocator/owner custody and
  emergency process;
- a documented user refund or failure-recovery path, including its liveness
  assumptions;
- removal or explicit deprecation of the full-allowance deposit overload.

No Relay address is copied into `chains.json`. That schema models DEX
factory/router pairs; Relay deployments are versioned API data with different
semantics.

## Other aggregator candidates

No candidate below is currently included. They remain separate research items:

| Candidate | Possible registry boundary | Required before inclusion |
| --- | --- | --- |
| Across | `SpokePool` deposit/event decoding | Pin each proxy implementation and admin, reconcile ABI licensing, and match the audited revision |
| Odos | Versioned router execution/decoding | Reproduce the deployed router bytecode and verify selectors, license, and current official deployment map |
| LI.FI / Socket | Route and bridge event decoding | Select a stable facet/module boundary; a synthetic all-in-one ABI would be incomplete or version-mixed |
| 0x / 1inch | Versioned swap execution/decoding | Pin the exact API-selected deployment and source revision; do not publish a timeless generic router |

This queue is not a safety endorsement. Each entry requires its own
chain-by-chain source, bytecode, proxy, permissions, audit, and license review
before code is added.
