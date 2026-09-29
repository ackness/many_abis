#!/usr/bin/env python3
"""Fetch a verified contract ABI through the fixed Etherscan V2 endpoint."""

import argparse
import json
import os
from pathlib import Path

import many_abis as ma


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chain_id", type=int, help="EVM chain ID")
    parser.add_argument("address", help="non-zero EVM contract address")
    parser.add_argument(
        "--output",
        type=Path,
        help="write formatted ABI JSON to this file instead of stdout",
    )
    arguments = parser.parse_args()

    api_key = os.environ.get("ETHERSCAN_API_KEY")
    if not api_key:
        parser.error("set ETHERSCAN_API_KEY in the environment")

    raw_abi = ma.get_abi_from_address(
        arguments.address,
        api_key,
        chain_id=arguments.chain_id,
    )
    if raw_abi is None:
        raise SystemExit(
            "Etherscan did not return a verified ABI; check the chain ID, "
            "address, API key, and network connectivity"
        )

    try:
        abi = json.loads(raw_abi)
    except json.JSONDecodeError as exc:
        raise SystemExit("Etherscan returned malformed ABI JSON") from exc
    if not isinstance(abi, list):
        raise SystemExit("Etherscan returned an ABI value that is not a JSON array")

    formatted = json.dumps(abi, indent=2, ensure_ascii=False) + "\n"
    if arguments.output is None:
        print(formatted, end="")
    else:
        arguments.output.write_text(formatted, encoding="utf-8")
        print("wrote {} ABI items to {}".format(len(abi), arguments.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
