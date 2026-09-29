#!/usr/bin/env python3
"""Inspect one chain's generated DEX and token catalog without network access."""

import argparse
import json
from typing import Any

import many_abis as ma


def build_summary(chain_slug: str) -> dict[str, Any]:
    chain = ma.get_chain(name=chain_slug)
    contracts = ma.list_contracts(chain=chain_slug)
    return {
        "chain": {
            "slug": chain_slug,
            "name": chain["name"],
            "chain_id": chain["chain_id"],
            "explorer": chain["explorer"],
            "official_rpcs": chain["rpc"],
        },
        "dex_contracts": [
            contract
            for contract in contracts
            if ":dex:" in contract["contract_id"]
        ],
        "tokens": ma.list_tokens(chain=chain_slug),
    }


def _print_human(summary: dict[str, Any]) -> None:
    chain = summary["chain"]
    print(
        "{} ({} / chain ID {})".format(chain["name"], chain["slug"], chain["chain_id"])
    )
    print("Explorer: {}".format(chain["explorer"]))
    print("Official RPCs: {}".format(len(chain["official_rpcs"])))

    print("\nDEX contracts:")
    for contract in summary["dex_contracts"]:
        print(
            "- {} [{}]: {} ({})".format(
                contract["name"],
                contract["role"],
                contract["address"],
                contract["provenance_status"],
            )
        )

    print("\nTokens:")
    for token in summary["tokens"]:
        print(
            "- {}: {} ({} decimals, {})".format(
                token["configured_symbol"],
                token["address"],
                token["decimals"],
                token["origin"],
            )
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--chain",
        choices=ma.all_chains(),
        default="base",
        help="chain slug to inspect (default: base)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="write machine-readable JSON instead of a summary",
    )
    arguments = parser.parse_args()

    summary = build_summary(arguments.chain)
    if arguments.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        _print_human(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
