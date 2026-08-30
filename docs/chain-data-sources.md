# Chain Data Sources and Verification

This document records the evidence and acceptance criteria used to maintain
`registry/chains/*.json`. The packaged `many_abis/assets/utils/chains.json` is
generated from those reviewed source files. This policy is intentionally
stricter than a list
of projects shown by an aggregator: an entry is added to the runtime data only
after its identity and deployed contracts can be independently verified.

## Acceptance criteria

- Chain metadata must come from the chain's official documentation.
- Default RPC endpoints are limited to official public endpoints and established
  public infrastructure providers. Every endpoint must return the configured
  chain ID from `eth_chainId` without an API key.
- Token addresses must appear in an issuer-maintained address list or official
  chain token list. Runtime defaults prefer current issuer-native or officially
  migrated assets; legacy bridge tokens are omitted unless there is a specific
  compatibility requirement.
- DEX contracts must appear in official deployment documentation. Their chain
  bytecode is checked with `eth_getCode`; explorer verification and proxy status
  are checked when the explorer exposes them.
- DEX Screener volume is a prioritization signal, not proof that a contract is
  official, maintained, or audited.

Contract authenticity and bytecode checks reduce address mistakes. They do not
constitute a smart-contract security audit or guarantee future safety.

## DEX Screener snapshot

Observed on 2026-08-30 from the linked DEX Screener chain and DEX pages. Volumes
are rolling 24-hour values and will change.

| Chain | Chain volume | Leading DEX volumes observed |
| --- | ---: | --- |
| [BSC](https://dexscreener.com/bsc) | $3.12B | [PancakeSwap](https://dexscreener.com/bsc/pancakeswap) $3.040B; [Uniswap](https://dexscreener.com/bsc/uniswap) $20.5M |
| [Robinhood](https://dexscreener.com/robinhood) | $1.14B | [Uniswap](https://dexscreener.com/robinhood/uniswap) $1.070B; [Ramses](https://dexscreener.com/robinhood/ramses) $14.8M |
| [Ethereum](https://dexscreener.com/ethereum) | $659.4M | [Uniswap](https://dexscreener.com/ethereum/uniswap) $558.3M; [Curve](https://dexscreener.com/ethereum/curve) $88.1M |
| [Base](https://dexscreener.com/base) | $453.7M | [Aerodrome](https://dexscreener.com/base/aerodrome) $302.4M; [Uniswap](https://dexscreener.com/base/uniswap) $109.6M; [PancakeSwap](https://dexscreener.com/base/pancakeswap) $36.6M |
| [HyperEVM](https://dexscreener.com/hyperevm) | $66.8M | [HyperSwap](https://dexscreener.com/hyperevm/hyperswap) $14.4M; [nest](https://dexscreener.com/hyperevm/nest) $5.8M |
| [Polygon](https://dexscreener.com/polygon) | $47.5M | [Uniswap](https://dexscreener.com/polygon/uniswap) $21.1M; [QuickSwap](https://dexscreener.com/polygon/quickswap) $12.4M |
| [Arbitrum](https://dexscreener.com/arbitrum) | $36.2M | [Uniswap](https://dexscreener.com/arbitrum/uniswap) $29.9M; [PancakeSwap](https://dexscreener.com/arbitrum/pancakeswap) $2.7M; [Camelot](https://dexscreener.com/arbitrum/camelot) $2.6M |
| [Avalanche](https://dexscreener.com/avalanche) | $24.9M | [PHARAOH](https://dexscreener.com/avalanche/pharaoh) $20.5M; [Uniswap](https://dexscreener.com/avalanche/uniswap) $1.4M |
| [Monad](https://dexscreener.com/monad) | $8.8M | [Uniswap](https://dexscreener.com/monad/uniswap) $584K; [PancakeSwap](https://dexscreener.com/monad/pancakeswap) $532K |
| [Optimism](https://dexscreener.com/optimism) | $7.2M | [Velodrome](https://dexscreener.com/optimism/velodrome) $6.2M |
| [Unichain](https://dexscreener.com/unichain) | $4.3M | [Uniswap](https://dexscreener.com/unichain/uniswap) $4.1M |
| [Sonic](https://dexscreener.com/sonic) | Not reported | [Shadow Exchange](https://dexscreener.com/sonic/shadow-exchange) $420K |
| [Berachain](https://dexscreener.com/berachain) | $346K | [Kodiak](https://dexscreener.com/berachain/kodiak) $343K |
| [Linea](https://dexscreener.com/linea) | $163K | [Etherex](https://dexscreener.com/linea/etherex) ranked first |

This snapshot explains selection priority only. A high-volume DEX is omitted if
official deployment evidence or a compatible factory/router representation is
not available.

The runtime set no longer includes MDEX, MMF, KoffeeSwap, Velodrome V1,
ApeSwap, BiSwap V2, or Trader Joe V1. These entries were either inactive in the
current-volume review, superseded by a current deployment, or outside the
popular-DEX focus. Their contracts may still have bytecode and historical
pools; removal is a default-data decision, not a claim that every historical
contract self-destructed.

DEX Screener did not expose X Layer on 2026-08-30: both candidate chain pages
returned `Page not Found`, its search API returned no X Layer pairs, and token
pair queries for the official WOKB address returned an empty result. This is an
unsupported-data condition, not evidence of zero volume. As an explicitly
labelled fallback, the [DeFiLlama X Layer DEX page](https://defillama.com/dexs/chain/x-layer)
and [API](https://api.llama.fi/overview/dexs/X-Layer?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true&dataType=dailyVolume)
reported $11.518M chain volume, led by Uniswap V3 at $8.855M and Uniswap V4 at
$2.960M. Kaliber and OkieSwap V3 were each below $112K. These rolling values
were observed at 2026-08-30 05:44 UTC and are used only for prioritization.

## Confirmed lifecycle changes

- HECO shut down on 2025-01-15 and is removed as a supported production chain.
- OKTChain was supported only through 2026-01-01 according to the
  [official OKX retirement notice](https://www.okx.com/en-us/help/announcement-on-the-pp-upgrade-of-x-layer-and-optimisation-of-the-okb-gas).
  It was the chain-ID-66 network with OKT as its native asset. X Layer is a
  separate chain-ID-196 network with OKB as its native asset; it is not a
  rename or in-place chain-ID migration of OKTChain.
- Moonriver announced a wind-down and required migration to Base by 2026-07-31
  in the [official Moonbeam notice](https://moonbeam.network/news/moonriver-strategic-update-movr-is-migrating-to-base/).
- Fantom Opera remains reachable, but new development moved to Sonic according
  to the [official migration documentation](https://docs.soniclabs.com/migration/overview).
  Fantom is removed from the current runtime set as a scope decision, not
  because its chain stopped producing blocks.
- KCC also remains reachable. It is removed from the current runtime set because
  it is outside the popular-chain focus and its defaults were bridge-issued
  KCC-Peg assets rather than issuer-native stablecoins.

## Confirmed stablecoin corrections

Circle's [official contract address list](https://developers.circle.com/stablecoins/usdc-contract-addresses)
is the source for native USDC deployments.

- Arbitrum: native `USDC` is
  `0xaf88d065e77c8cC2239327C5EDb3A432268e5831`; `USDC.e` is omitted.
- Avalanche: native `USDC` is
  `0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E`; bridged `.e` assets are omitted.
- Cronos: native `USDC` is
  `0x3D7F2C478aAfdB65542BCB44bCeeC05849999d2D`; the former `0xc212...`
  entry is USDC.e and is omitted.
- Polygon: native `USDC` is
  `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359`; `USDC.e` is omitted.
- Optimism: native `USDC` is
  `0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85`; `USDC.e` is omitted.

The [USDT0 deployment API](https://docs.usdt0.to/api/deployments) is the source
for the migrated `USDT0` defaults on Arbitrum, Optimism, Polygon, HyperEVM,
Unichain, and X Layer. Optimism's retired sUSD and old bridged USDT are not
runtime defaults. BSC's USDC and USDT entries are named `USDC.binance-peg` and
`USDT.binance-peg` so they cannot be mistaken for issuer-native contracts.

BUSD remains a historical token contract, but Paxos stopped minting it and has
wound down the product. It is not treated as a current default stablecoin; see
the [Paxos notice](https://www.paxos.com/newsroom/paxos-will-halt-minting-new-busd-tokens).

The following additional stablecoins were selected from issuer-maintained
sources and independently checked for bytecode, symbol, decimals, and supply on
2026-08-30:

| Chain | Symbol | Address | Issuer evidence | Supply snapshot |
| --- | --- | --- | --- | ---: |
| Ethereum | USDS | `0xdC035D45d973E3EC169d2276DDab16f1e407384F` | [Sky Protocol](https://developers.skyeco.com/guides/skylink/usds-ethereum-solana-bridge/) | 6.680B |
| Ethereum | USDe | `0x4c9EDD5852cd905f086C759E8383e09bff1E68B3` | [Ethena](https://docs.ethena.fi/api-documentation/overview) | 4.076B |
| Ethereum | PYUSD | `0x6c3ea9036406852006290770BEdFcAbA0e23A0e8` | [Paxos](https://docs.paxos.com/guides/stablecoin/pyusd/mainnet) | 1.795B |
| Ethereum | USD1 | `0x8d0D000Ee44948FC98c9B98A4FA4921476f08B0d` | [BitGo reserve report](https://landing.bitgo.com/rs/552-OGK-141/images/USD1_Reserve_Attestation_Report_March_2026.pdf) | 1.561B |
| BSC | USD1 | `0x8d0D000Ee44948FC98c9B98A4FA4921476f08B0d` | [BitGo reserve report](https://landing.bitgo.com/rs/552-OGK-141/images/USD1_Reserve_Attestation_Report_March_2026.pdf) | 1.397B |
| BSC | FDUSD | `0xc5f0f7b66764F6ec8C8Dff7BA683102295E16409` | [First Digital](https://www.firstdigitallabs.com/fdusd) | 57.236M |
| HyperEVM | USDT0 | `0xB8CE59FC3717ada4C02eaDF9682A9e934F625ebb` | [USDT0](https://usdt0.to/ecosystem/hyperliquid) | 104.472M |
| Robinhood | USDG.oft | `0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168` | [Paxos](https://docs.paxos.com/guides/stablecoin/usdg/mainnet) | 436.160M |

X Layer was checked against newer issuer and protocol sources because its
official general contract table still includes legacy bridged assets. Only the
following current defaults were admitted:

| Symbol | Address | Current evidence | On-chain supply snapshot |
| --- | --- | --- | ---: |
| USDC | `0xB6CEceAB302E2E4948951eE7843FC24E92933061` | [Circle native-USDC launch](https://www.circle.com/blog/now-available-native-usdc-cctp-on-x-layer) | 12.320M |
| USDT0 | `0x779Ded0c9e1022225f8E0630b35a9b54bE713736` | [USDT0 X Layer page](https://usdt0.to/ecosystem/x-layer); [OKX migration FAQ](https://www.okx.com/en-us/help/usdt0-faq) | 114.234M |
| USDG | `0x4ae46a509F6b1D9056937BA4500cb143933D2dc8` | [Paxos mainnet address list](https://docs.paxos.com/guides/stablecoin/usdg/mainnet) | 1.790B |

Circle identifies `0x74b7...6d22` as non-Circle-issued `USDC_Bridged`, while
OKX identifies `0x1E4a...D41d` as the old wrapped USDT being phased out in
favor of USDT0. Neither legacy address is exposed as the default `USDC` or
`USDT` entry. The low-supply `USDC.e` and DAI bridge contracts are also omitted
from the default set.

The eight pre-X-Layer entries in the first table have the following risk
profile: `USDT0` is a burn-and-mint cross-chain representation. Robinhood's `USDG.oft`
is the LayerZero OFT deployment documented by Paxos; the suffix prevents it
from being mistaken for the L1 token. With the exception of USDe, these newly
added contracts are upgradeable proxies. USDe instead has privileged
owner/minter roles. These are issuer and governance risks even when the address
and current implementation are verified.

The three X Layer defaults are also upgradeable proxies. Their currently
resolved implementations have non-empty bytecode, but issuer, bridge, and
upgrade-governance risk remains.

## New-chain evidence

The following mainnet metadata is confirmed by official chain documentation.
DEX deployment provenance and bytecode are a separate admission gate.

| Chain | Chain ID | Official public RPC | Explorer | Wrapped native | Issuer/chain-confirmed stablecoin |
| --- | ---: | --- | --- | --- | --- |
| [Base](https://docs.base.org/base-chain/quickstart/connecting-to-base) | 8453 | `https://mainnet.base.org` | [Base Blockscout](https://base.blockscout.com/) | WETH `0x4200000000000000000000000000000000000006` | USDC `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| [HyperEVM](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/hyperevm) | 999 | `https://rpc.hyperliquid.xyz/evm` | [HyperEVM Scan](https://hyperevmscan.io/) | WHYPE `0x5555555555555555555555555555555555555555` | USDC `0xb88339CB7199b77E23DB6E890353E22632Ba630f` |
| [Robinhood Chain](https://docs.robinhood.com/chain/connecting/) | 4663 | `https://rpc.mainnet.chain.robinhood.com` | [Robinhood Blockscout](https://robinhoodchain.blockscout.com/) | WETH `0x0Bd7D308f8E1639FAb988df18A8011f41EAcAD73` | USDG `0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168` |
| [Monad](https://docs.monad.xyz/developer-essentials/network-information/index.md) | 143 | `https://rpc.monad.xyz` | [MonadVision](https://monadvision.com/) | WMON `0x3bd359C1119dA7Da1D913D1C4D2B7c461115433A` | USDC `0x754704Bc059F8C67012fEd69BC8A327a5aafb603` |
| [Sonic](https://docs.soniclabs.com/sonic/build-on-sonic/getting-started) | 146 | `https://rpc.soniclabs.com` | [SonicScan](https://sonicscan.org/) | wS `0x039e2fB66102314Ce7b64Ce5Ce3E5183bc94aD38` | USDC `0x29219dd400f2Bf60E5a23d13Be72B486D4038894` |
| [Berachain](https://docs.berachain.com/build/getting-started/common-resources) | 80094 | `https://rpc.berachain.com` | [BeraScan](https://berascan.com/) | WBERA `0x6969696969696969696969696969696969696969` | BUSD `0xFCBD14DC51f0A4d49d5E53C2E0950e0bC26d0Dce` |
| [Unichain](https://developers.uniswap.org/docs/unichain/technical-information/network-information) | 130 | `https://mainnet.unichain.org` | [Uniscan](https://uniscan.xyz/) | WETH `0x4200000000000000000000000000000000000006` | USDC `0x078D782b760474a361dDA0AF3839290b0EF57AD6` |
| [Linea](https://docs.linea.build/network/build/connect) | 59144 | `https://rpc.linea.build` | [LineaScan](https://lineascan.build/) | WETH `0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f` | USDC `0x176211869cA2b568f2A7D4EE941E073a821EE1ff` |
| [X Layer](https://web3.okx.com/onchainos/dev-docs/xlayer/developer/build-on-xlayer/network-information) | 196 | `https://rpc.xlayer.tech`, `https://xlayerrpc.okx.com` | [OKX Explorer](https://www.okx.com/web3/explorer/xlayer) | WOKB `0xe538905cf8410324e03A5A23C1c177a474D59b2b` | native USDC `0xB6CEceAB302E2E4948951eE7843FC24E92933061` |

Base, Robinhood Chain, Monad, Sonic, Unichain, and X Layer passed the complete
runtime gate, including an official DEX deployment. HyperEVM remains supported
for chain and token metadata, but its HyperSwap entry is omitted because an
exact redistributable official router ABI was not established. Berachain and
Linea remain documented research candidates but are not added to `chains.json`
in this release because their observed DEX volume was lower and no DEX contract
set was independently admitted in this review.

Robinhood Chain mainnet is live with chain ID 4663. Its testnet uses chain ID
46630 and must not be mixed into the mainnet entry. The official
[token-contract page](https://docs.robinhood.com/chain/contracts/) and the
[Paxos USDG deployment page](https://docs.paxos.com/guides/stablecoin/usdg/mainnet)
independently identify its WETH and USDG contracts.

### On-chain and explorer verification snapshot

Checked on 2026-08-30. Every official RPC URL in the nine-chain research table
returned the configured chain ID. Every admitted wrapped-native and stablecoin
address returned non-empty runtime bytecode, and its `name()`, `symbol()`, and
`decimals()` values matched the documented identity.

- Base, HyperEVM, Sonic, Unichain, and Linea explorers show source-verified
  contracts for both token addresses.
- X Layer's explorer identifies verified WOKB, native USDC, USDT0, and USDG
  contracts. The stablecoins are proxies; their current implementations were
  independently resolved and checked for bytecode.
- Robinhood Blockscout shows verified contracts, but both WETH and USDG are
  upgradeable proxies. Their current implementations were also identified by
  the explorer. This is an upgrade-governance risk, not an address mismatch.
- MonadVision shows the correct WMON and USDC identities, but an address-level
  source-verification claim was not visible; their explorer verification status
  therefore remains unknown.
- Berachain's stablecoin returns `Bera USD` / `BUSD` on-chain while an older
  explorer name tag still says `HONEY Token`. The runtime metadata is used, and
  the historical label is not treated as a separate token.

Official public RPCs can be rate-limited and are intended as safe defaults for
light reads, not as production SLA endpoints or archive providers.

## Default RPC verification

Every RPC retained in `chains.json` returned its configured chain ID from
`eth_chainId` on 2026-08-30. Most chains now use only their official public
endpoint. The limited exceptions are documented public infrastructure:

- Ethereum has no protocol-operated public RPC, so the default is PublicNode.
- BSC and Cronos use their official endpoint plus a PublicNode fallback.
- Polygon uses dRPC, 1RPC, and PublicNode endpoints listed by Polygon's
  [current RPC documentation](https://docs.polygon.technology/pos/reference/rpc-endpoints/).
- X Layer retains both public endpoints listed by its
  [official RPC documentation](https://web3.okx.com/onchainos/dev-docs/xlayer/developer/rpc-endpoints/rpc-endpoints);
  both returned chain ID 196.

Anonymous legacy endpoints, MEV submission endpoints, and endpoints requiring
an API key were removed. In particular, the tested Ankr URLs returned no
unauthenticated result, and the tested LlamaRPC Ethereum endpoint returned HTTP
521, so neither remains a default.

## Confirmed DEX deployments

These entries passed the official-deployment and non-empty-bytecode gates. ABI
families remain explicit because similarly named `factory` and `router`
contracts are not interchangeable across protocol designs.

| Chain / DEX | Factory | Router | Protocol evidence |
| --- | --- | --- | --- |
| Cronos / VVS Finance V2 | `0x3B44B2a187a7b3824131F8db5a74194D0a42Fc15` | `0x145863Eb42Cf62847A6Ca784e6416C1682b1b2Ae` | [Official VVS contract page](https://docs.vvs.finance/docs/smart-contracts-and-security); the router returns the configured factory and WCRO on-chain |
| Base / Aerodrome Slipstream Gauges V3 | `0xf8f2eB4940CFE7d13603DDDD87f123820Fc061Ef` | `0x698Cb2b6dd822994581fEa6eA4Fc755d1363A92F` | [Official deployment table](https://github.com/aerodrome-finance/slipstream#deployments); Sourcify exact-match metadata identifies `CLFactory` and `SwapRouter` |
| Base / Uniswap V3 | `0x33128a8fC17869897dcE68Ed026d694621f6FDfD` | `0x2626664c2603336E57B271c5C0b26F421741e481` | [Official deployment page](https://developers.uniswap.org/docs/protocols/v3/deployments/v3-base-deployments); Base Blockscout identifies verified `UniswapV3Factory` and `SwapRouter02` contracts |
| Base / PancakeSwap V3 | `0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865` | `0x1b81D678ffb9C0263b24A97847620C99d213eB14` | [Official address page](https://developer.pancakeswap.finance/contracts/v3/addresses); Base Blockscout identifies verified `PancakeV3Factory` and `SwapRouter` contracts |
| Robinhood / Uniswap V3 | `0x1f7d7550b1b028f7571e69a784071f0205fd2efa` | `0xcaf681a66d020601342297493863e78c959e5cb2` | [Official deployment page](https://developers.uniswap.org/docs/protocols/v3/deployments/v3-robinhood-chain-deployments); Robinhood Blockscout identifies verified `UniswapV3Factory` and `SwapRouter02` contracts |
| BSC / Uniswap V3 | `0xdB1d10011AD0Ff90774D0C6Bb92e5C5c8b4461F7` | `0xB971eF87ede563556b2ED4b1C0b0019111Dd85d2` | [Official deployment page](https://developers.uniswap.org/docs/protocols/v3/deployments/v3-bnb-deployments); BscScan identifies exact-match `UniswapV3Factory` and `SwapRouter02` source |
| Monad / Uniswap V3 | `0x204faca1764b154221e35c0d20abb3c525710498` | `0xfe31f71c1b106eac32f1a19239c9a9a72ddfb900` | [Official deployment page](https://developers.uniswap.org/docs/protocols/v3/deployments/v3-monad-deployments) |
| Sonic / Shadow CLMM | `0xcD2d0637c94fe77C2896BbCBB174cefFb08DE6d7` | `0x5543c6176feb9b4b179078205d7c29eea2e2d695` | [Official address page](https://docs.shadow.so/pages/contract-addresses); SonicScan identifies verified `Shadow V3 Factory` and `Swap Router` contracts |
| Unichain / Uniswap V3 | `0x1f98400000000000000000000000000000000003` | `0x73855d06de49d0fe4a9c42636ba96c62da12ff9c` | [Official deployment page](https://developers.uniswap.org/docs/protocols/v3/deployments/v3-unichain-deployments) |
| X Layer / Uniswap V3 | `0x4B2ab38DBF28D31D467aA8993f6c2585981D6804` | `0x4f0C28f5926AFDA16bf2506D5D9e57Ea190f9bcA` | [Official deployment page](https://developers.uniswap.org/docs/protocols/v3/deployments/v3-xlayer-deployments); Uniswap's machine-readable deployment feed marks both contracts active on chain ID 196; OKLink identifies the factory and `SwapRouter02` |
| Optimism / Velodrome Slipstream | `0xe13Dd1fbA721Aa81a1826D9523AC9BC7d260c879` | `0xbA3aEe516399388C779463183d00bB579f5041Ca` | [Official deployment table](https://github.com/velodrome-finance/slipstream#deployment) |
| Ethereum / Uniswap V3 | `0x1F98431c8aD98523631AE4a59f267346ea31F984` | `0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45` | [Official deployment page](https://developers.uniswap.org/docs/protocols/v3/deployments/v3-ethereum-deployments) |
| Arbitrum / Uniswap V3 | `0x1F98431c8aD98523631AE4a59f267346ea31F984` | `0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45` | [Official deployment page](https://developers.uniswap.org/docs/protocols/v3/deployments/v3-arbitrum-deployments) |
| Optimism / Uniswap V3 | `0x1F98431c8aD98523631AE4a59f267346ea31F984` | `0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45` | [Official deployment page](https://developers.uniswap.org/docs/protocols/v3/deployments/v3-optimism-deployments) |
| Polygon / Uniswap V3 | `0x1F98431c8aD98523631AE4a59f267346ea31F984` | `0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45` | [Official deployment page](https://developers.uniswap.org/docs/protocols/v3/deployments/v3-polygon-deployments) |
| Avalanche / LFJ Liquidity Book V2.2 | `0xb43120c4745967fa9b93E79C149E66B0f2D6Fe0c` | `0x18556DA13313f3532c54711497A8FedAC273220E` | [Official deployment page](https://developers.lfj.gg/deployment-addresses/avalanche) |

Uniswap V4 is deliberately excluded from the legacy factory/router schema. V4
uses a `PoolManager`, and recording it as a factory would give callers incorrect
ABI semantics. This also applies to X Layer even though V4 ranked second in the
fallback volume snapshot. Aerodrome Slipstream, Velodrome Slipstream, Shadow
CLMM, and LFJ use their own bundled ABI families rather than the repository's
Uniswap or old Joe ABI files. HyperSwap is omitted under the stricter exact-ABI
and redistribution-license gate.

## Bundled ABI provenance

The newly bundled protocol-specific ABIs are the verified deployed-contract
interfaces, not hand-written approximations:

| ABI family | Verification source | Upstream source/license |
| --- | --- | --- |
| LFJ Liquidity Book V2.2 | [Factory on Sourcify](https://sourcify.dev/server/v2/contract/43114/0xb43120c4745967fa9b93E79C149E66B0f2D6Fe0c?fields=abi,metadata), [router on RouteScan](https://api.routescan.io/v2/network/mainnet/evm/43114/etherscan/api?module=contract&action=getabi&address=0x18556DA13313f3532c54711497A8FedAC273220E) | [LFJ joe-v2](https://github.com/lfj-gg/joe-v2), MIT |
| Aerodrome Slipstream Gauges V3 | Sourcify exact-match metadata for the factory and router linked in the deployment table | [Aerodrome Slipstream](https://github.com/aerodrome-finance/slipstream), contract files identify GPL-2.0-or-later; repository licensing terms also apply |
| Velodrome Slipstream | [Factory](https://sourcify.dev/server/v2/contract/10/0xe13Dd1fbA721Aa81a1826D9523AC9BC7d260c879?fields=abi,metadata), [router](https://sourcify.dev/server/v2/contract/10/0xbA3aEe516399388C779463183d00bB579f5041Ca?fields=abi,metadata) exact matches | [Velodrome Slipstream](https://github.com/velodrome-finance/slipstream), contract files identify GPL-2.0-or-later; repository licensing terms also apply |
| Shadow CLMM V3 | SonicScan Exact Match ABI for the configured factory and router | [Shadow core](https://github.com/Shadow-Exchange/shadow-core), relevant contract files identify GPL-2.0-or-later |
| PancakeSwap V3 | Sourcify verified metadata for the BSC `PancakeV3Factory`, BSC `SmartRouter`, Base `PlunderV3Factory`, and Base `SwapRouter` deployments | [PancakeSwap v3 contracts](https://github.com/pancakeswap/pancake-v3-contracts), GPL-2.0-or-later |
| Uniswap V1 Exchange | Official ABI at fixed commit `c10c08d` | [Uniswap v1-contracts](https://github.com/Uniswap/v1-contracts/blob/c10c08d81d6114f694baa8bd32f555a40f6264da/abi/uniswap_exchange.json), GPL-3.0-only |
| Aave V2 LendingPoolAddressesProvider | Official package artifact | [`@aave/protocol-v2@1.0.1`](https://www.npmjs.com/package/@aave/protocol-v2/v/1.0.1), AGPL-3.0-or-later |

The Slipstream and Shadow routers use `int24 tickSpacing`; Uniswap V3 uses
`uint24 fee`. Those types produce different selectors, so the interfaces must
not be interchanged. The Base Pancake deployment also has its own factory ABI
because the verified target is `PlunderV3Factory`.

The deprecated `0xE592...` SwapRouter01 is no longer a runtime default. The
bundled `UNISWAP_V3_ROUTER_02` ABI was extracted from version 1.3.1 of the
official [`@uniswap/swap-router-contracts`](https://www.npmjs.com/package/@uniswap/swap-router-contracts/v/1.3.1)
artifact. Entries using `SwapRouter02` explicitly reference this ABI; they must
not use the older deadline-bearing `UNISWAP_V3_ROUTER` interface.

During the 0.3 registry migration, three historical copy errors were detected
and replaced from fixed official artifacts without changing their public ABI
names: `PANCAKE_V3_POOL_V3` had contained a factory ABI,
`AAVE_V2_LENDING_POOL_ADDRESSES_PROVIDER` had contained the Aave V1 core ABI,
and `UNISWAP_V1_EXCHANGE` had contained an Aave incentive-provider ABI. Tests
now require identity-specific signatures for all three. The remaining
pre-0.3 ABI assets without complete provenance are hash-pinned in the explicit
legacy allowlist and cannot change silently.
