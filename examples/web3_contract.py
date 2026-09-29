#!/usr/bin/env python3
"""Use a registered address and ABI with the optional web3.py package."""

import argparse
import os
from copy import deepcopy

import many_abis as ma


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    try:
        from web3 import Web3
    except ImportError as exc:
        raise SystemExit(
            "install the optional dependency first: pip install web3"
        ) from exc

    chain = ma.get_chain(name="base")
    router_record = ma.get_contract("base:dex:uniswap-v3:router")
    factory_record = ma.get_contract("base:dex:uniswap-v3:factory")

    # Use RPC_URL when supplied; otherwise use the first reviewed official RPC.
    rpc_url = os.environ.get("RPC_URL") or chain["rpc"][0]
    web3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 15}))
    if not web3.is_connected():
        raise SystemExit("could not connect to the configured Base RPC")

    router = web3.eth.contract(
        address=Web3.to_checksum_address(router_record["address"]),
        abi=deepcopy(ma.get_abi(router_record["abi"])),
    )
    observed_factory = router.functions.factory().call()
    expected_factory = Web3.to_checksum_address(factory_record["address"])
    if observed_factory != expected_factory:
        raise SystemExit(
            "router factory mismatch: expected {}, observed {}".format(
                expected_factory, observed_factory
            )
        )

    print("Base Uniswap V3 router: {}".format(router.address))
    print("factory() matches the registered address: {}".format(observed_factory))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
