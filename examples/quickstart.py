#!/usr/bin/env python3
"""Offline quickstart for ABI, chain, contract, token, and evidence lookups."""

from copy import deepcopy

import many_abis as ma


def main() -> int:
    print("many-abis {}".format(ma.__version__))
    print("supported chains: {}".format(", ".join(ma.all_chains())))

    # Chain and catalog helpers return defensive copies.
    base = ma.get_chain(name="base")
    print("chain: {} (chain ID {})".format(base["name"], base["chain_id"]))

    router = ma.get_contract("base:dex:uniswap-v3:router")
    usdc = ma.get_token("base", "USDC")
    snapshot = ma.get_verification("base", router["address"])
    print("router: {} @ {}".format(router["name"], router["address"]))
    print(
        "token: {} @ {} ({} decimals, {})".format(
            usdc["configured_symbol"],
            usdc["address"],
            usdc["decimals"],
            usdc["origin"],
        )
    )
    print(
        "pinned evidence: block {} / code hash {}".format(
            snapshot["block_number"], snapshot["runtime_code_keccak256"]
        )
    )

    # ABI values are lazy and recursively read-only. Deep-copy before mutation.
    ma.clear_abi_cache()
    router_abi = ma.get_abi(router["abi"])
    mutable_abi = deepcopy(router_abi)
    abi_info = ma.get_abi_info(router["abi"])
    print("loaded ABIs: {}".format(", ".join(ma.loaded_abis())))
    print(
        "ABI: {} ({} items, {}, sha256 {})".format(
            router["abi"],
            len(mutable_abi),
            abi_info["license"]["spdx_expression"],
            abi_info["canonical_sha256"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
