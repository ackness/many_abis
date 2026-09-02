# Bundled license texts

The root `LICENSE` applies to original `many-abis` Python code. ABI data is
derived from third-party projects and remains subject to the per-entry terms
and immutable sources recorded in `THIRD_PARTY_NOTICES.md`.

The distribution includes the standard or upstream license texts needed by
the verified ABI set:

| Recorded SPDX expression | Included text |
| --- | --- |
| `MIT` (OpenZeppelin) | `MIT-OpenZeppelin.txt` |
| `MIT` (Chainlink) | `MIT-Chainlink.txt` |
| `MIT` (Multicall3) | `MIT-Multicall3.txt` |
| `MIT` (Permit2) | `MIT-Permit2.txt` |
| `MIT` (LFJ) | `MIT-LFJ.txt` |
| `GPL-2.0-or-later` | `GPL-2.0.txt` |
| `GPL-3.0-only`, `GPL-3.0-or-later` | `GPL-3.0.txt` |
| `AGPL-3.0-or-later` | `AGPL-3.0.txt` |
| `BUSL-1.1` for Uniswap V3 Core | `BUSL-1.1.txt` |

The GNU texts were obtained from the Free Software Foundation at
`https://www.gnu.org/licenses/`. The BUSL text is the upstream Uniswap V3 Core
license at commit `ed88be38ab2032d82bf10ac6f8d03aa631889d48`. The MIT texts
are verbatim license records from OpenZeppelin `v5.6.1`, Chainlink
`contracts-v1.5.0` (the MIT portion applicable to the interface), Multicall3
commit `a1fa0644fa412cd3237ef7081458ecb2ffad7dbe`, Permit2 commit
`cc306b601f172c51bc04334a109e98340456620b`, and LFJ Joe V2 commit
`067c6ccf5b8ff1526d03fa3e4c65ec45d01c1f73`.
Inclusion of a license text records applicable terms; it is not a security
audit or a legal conclusion about an ABI.

Legacy ABI files with unresolved provenance or licensing are quarantined in
the source repository and are not included in wheel or sdist artifacts.
