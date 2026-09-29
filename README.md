# Many Abis

![Version](https://img.shields.io/badge/many--abis-v0.4.0-green)
![Pypi](https://img.shields.io/pypi/dm/many-abis)

![GitHub Org's stars](https://img.shields.io/github/stars/ackness/many_abis?style=social)
![GitHub forks](https://img.shields.io/github/forks/ackness/many_abis?style=social)

---

Verified ABI files, EVM chain metadata, contract addresses, token records, and
pinned on-chain evidence for blockchain developers.

---

Supported DEX deployments:

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

Python 3.13 or newer is required.

```bash
uv add many-abis

# pip remains supported when integrating with a non-uv project.
python -m pip install --upgrade many-abis
```

## Quick start

```python
import many_abis as ma

# Chain, contract, and token lookups return defensive copies.
base = ma.get_chain(name="base")
router = ma.get_contract("base:dex:uniswap-v3:router")
usdc = ma.get_token("base", "USDC")
snapshot = ma.get_verification("base", usdc["address"])

print(base["chain_id"], base["rpc"])
print(router["address"], router["provenance_status"])
print(usdc["origin"], usdc["decimals"])
print(snapshot["block_number"], snapshot["runtime_code_keccak256"])

# ABI files are loaded lazily and cached as recursively read-only values.
router_abi = ma.get_abi(router["abi"])
abi_info = ma.get_abi_info(router["abi"])
print(len(router_abi), abi_info["canonical_sha256"])
print(ma.loaded_abis())

# Filter the generated catalogs without accessing the network.
print(ma.list_contracts(chain="base", role="router"))
print(ma.list_tokens(chain="base", role="stablecoin"))
print(ma.find_abis(contract_role="router"))
```

Use `copy.deepcopy()` before changing an ABI. The public `ABIS` and `CHAINS`
registries are intentionally read-only so one caller cannot corrupt cached
state for the rest of a process.

To retrieve an ABI that is not bundled, use an API key from the environment and
pass an EVM chain ID. The request always uses the fixed Etherscan V2 endpoint:

```python
import os

import many_abis as ma

abi_json = ma.get_abi_from_address(
    "0x2626664c2603336E57B271c5C0b26F421741e481",
    os.environ["ETHERSCAN_API_KEY"],
    chain_id=8453,
)
```

Complete runnable examples cover offline catalog inspection, safe Etherscan
lookup, and optional `web3.py` integration in the
[examples directory](https://github.com/ackness/many_abis/tree/main/examples).

## Registry maintenance

Runtime data is generated offline. Edit one reviewed source file under
`registry/chains/` or `registry/abi-metadata.json`, then regenerate and verify:

```bash
uv sync --locked --dev
uv run python scripts/generate_registry.py --write
uv run python scripts/generate_registry.py --check
uv run python -m unittest discover -s tests -v
uv run mypy
```

On-chain evidence refreshes are explicit network operations and are separate
from the offline generator. Refresh only through the reviewed RPC list, inspect
the diff, and then regenerate:

```bash
uv run python scripts/refresh_verifications.py --chain base --write
uv run python scripts/generate_registry.py --write
```

Do not edit `many_abis/assets/utils/chains.json`, `abi-index.json`, generated
documentation, or `many_abis/abis.pyi` directly. Generation is deterministic
and never accesses the network. See the generated [chain registry](https://github.com/ackness/many_abis/blob/main/docs/generated/supported-chains.md),
[ABI provenance](https://github.com/ackness/many_abis/blob/main/docs/generated/abi-provenance.md), and the detailed
[verification policy](https://github.com/ackness/many_abis/blob/main/docs/chain-data-sources.md). Usage-specific caveats for
standards, oracles, multicall, Permit2, and proxy events are documented in
[common contract ABIs](https://github.com/ackness/many_abis/blob/main/docs/common-contract-abis.md). API-driven bridge and
aggregator boundaries are documented in
[cross-chain aggregators](https://github.com/ackness/many_abis/blob/main/docs/cross-chain-aggregators.md).
The generated contract/token catalogs, snapshot semantics, proxy limitations,
and query API are documented in
[registry verification](https://github.com/ackness/many_abis/blob/main/docs/registry-verification.md).
Pre-0.3 ABI files without complete provenance are quarantined under
`registry/legacy-abis/` and are not included in the runtime package or PyPI
artifacts. Public ABIs require verified provenance, an immutable source
reference, license evidence, and required function/event signatures.

## Build and release

Project metadata, runtime dependencies, and development dependencies live in
`pyproject.toml`; `uv.lock` pins the complete development environment. Build
both distribution formats from a clean commit with:

```bash
uv sync --locked --dev
uv run python scripts/build_release_artifacts.py --output-dir dist
uv run python scripts/check_distribution.py dist
uv run twine check dist/*
```

The release builder invokes `uv build --no-sources` twice from independent Git
archives and rejects non-identical outputs. GitHub Actions publishes the checked
artifacts with `uv publish --trusted-publishing always`, PyPI Trusted Publishing,
and PEP 740 attestations. Publishing requires GitHub's OIDC identity; no PyPI API
token or GitHub repository secret is needed.

### One-time Trusted Publisher setup

1. In the GitHub repository's **Settings > Environments**, create an environment
   named `pypi`. If deployment rules restrict refs, allow release tags such as
   `v*`. Required reviewers introduce a manual approval before publishing; omit
   them if releases should publish automatically.
2. Open the PyPI project's
   [Publishing settings](https://pypi.org/manage/project/many-abis/settings/publishing/)
   and add a GitHub Trusted Publisher with these exact values:

   | Field | Value |
   | --- | --- |
   | Owner | `ackness` |
   | Repository name | `many_abis` |
   | Workflow name | `python-publish.yml` |
   | Environment name | `pypi` |

   The workflow name is the filename, without `.github/workflows/`, rather than
   its display name. If the PyPI project does not exist yet, register a pending
   publisher in [Your publishing settings](https://pypi.org/manage/account/publishing/)
   with project name `many-abis` and the same values.

See the official [PyPI Trusted Publisher setup guide](https://docs.pypi.org/trusted-publishers/adding-a-publisher/)
and [uv GitHub Actions guide](https://docs.astral.sh/uv/guides/integration/github/#publishing-to-pypi).

### Publish a release

Commit and push the release files, including the workflow and `uv.lock`. Set
`project.version` in `pyproject.toml` to the new version, and refresh `uv.lock`
with `uv lock`. The runtime version comes from installed package metadata.
Create a matching tag, such as `v0.4.0` for
version `0.4.0`, on that commit, then **publish a GitHub Release** for the tag.
Pushing a tag alone or saving a draft release does not trigger publishing.
Published prereleases also trigger this workflow; use a matching prerelease
package version such as `0.4.1rc1` and tag `v0.4.1rc1`.

The workflow tests Python 3.13 and 3.14, checks the tag against the package
version, builds and validates the wheel and source distribution, then publishes
those artifacts from a separate job with `id-token: write`. A failed check
blocks publication. PyPI does not allow overwriting a published distribution;
use a new version for a changed release.

## License and provenance

Original Python code is MIT-licensed. Bundled verified ABI data remains subject
to its recorded upstream terms. See
[THIRD_PARTY_NOTICES.md](https://github.com/ackness/many_abis/blob/main/THIRD_PARTY_NOTICES.md)
and the license texts shipped under `LICENSES/`. Quarantined legacy ABI files
have unresolved provenance or licensing and are not part of the distribution.
