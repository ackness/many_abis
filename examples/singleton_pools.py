#!/usr/bin/env python3
"""Read singleton DEX pool state, quote one pool, or decode a supplied log."""

import argparse
import json
import os
from copy import deepcopy
from pathlib import Path

import many_abis as ma


PROTOCOLS = {
    "uniswap-v4": "uniswap-v4",
    "pancake-infinity-cl": "pancake-infinity-cl",
    "pancake-infinity-bin": "pancake-infinity-bin",
}
V4_FIELDS = ("currency0", "currency1", "fee", "tickSpacing", "hooks")
INFINITY_FIELDS = (
    "currency0", "currency1", "hooks", "poolManager", "fee", "parameters"
)


def parser_for_cli():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("state", "quote", "decode-log"):
        command = commands.add_parser(name)
        command.add_argument("--protocol", choices=tuple(PROTOCOLS), required=True)
        command.add_argument("--chain", required=True, help="Registry chain slug")
        if name != "decode-log":
            command.add_argument("--rpc-url", help="Overrides RPC_URL and registry RPC")
            command.add_argument(
                "--block", type=int,
                help="Block number; defaults to one sampled latest block",
            )
        if name == "state":
            command.add_argument("--pool-id", required=True, help="32-byte pool ID")
        elif name == "quote":
            command.add_argument("--pool-key-file", required=True, type=Path)
            direction = command.add_mutually_exclusive_group(required=True)
            direction.add_argument("--zero-for-one", dest="zero_for_one", action="store_true")
            direction.add_argument("--one-for-zero", dest="zero_for_one", action="store_false")
            command.add_argument("--amount-in", required=True, type=int, help="Atomic input units")
            command.add_argument("--hook-data", default="0x", help="Hex bytes passed to hooks")
            command.add_argument("--from-address", help="eth_call sender, if hook behavior depends on it")
        else:
            command.add_argument("--log-file", required=True, type=Path)
    return parser


def _web3():
    try:
        from web3 import Web3
        from hexbytes import HexBytes
    except ImportError as exc:
        raise ValueError("install the optional dependency first: pip install web3") from exc
    return Web3, HexBytes


def _record(chain, protocol, role):
    return ma.get_contract(f"{chain}:dex:{protocol}:{role}")


def _contract(w3, record):
    Web3, _ = _web3()
    return w3.eth.contract(
        address=Web3.to_checksum_address(record["address"]),
        abi=deepcopy(ma.get_abi(record["abi"])),
    )


def _bytes32(value, label, HexBytes):
    try:
        result = HexBytes(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be 0x-prefixed hex") from exc
    if not isinstance(value, str) or not value.startswith("0x") or len(result) != 32:
        raise ValueError(f"{label} must be 32 bytes of 0x-prefixed hex")
    return result


def _hex_bytes(value, label, HexBytes):
    if not isinstance(value, str) or not value.startswith("0x"):
        raise ValueError(f"{label} must be 0x-prefixed hex")
    try:
        return HexBytes(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be 0x-prefixed hex") from exc


def _pool_key(raw, protocol, Web3, HexBytes):
    fields = V4_FIELDS if protocol == "uniswap-v4" else INFINITY_FIELDS
    if not isinstance(raw, dict) or set(raw) != set(fields):
        raise ValueError(f"PoolKey must contain exactly: {', '.join(fields)}")
    key = {}
    for name in fields:
        value = raw[name]
        if name in ("currency0", "currency1", "hooks", "poolManager"):
            if not isinstance(value, str) or not Web3.is_address(value):
                raise ValueError(f"{name} must be a 20-byte EVM address")
            key[name] = Web3.to_checksum_address(value)
        elif name == "parameters":
            key[name] = _bytes32(value, name, HexBytes)
        else:
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{name} must be an integer")
            if name == "fee":
                max_fee = 100_000 if protocol == "pancake-infinity-bin" else 1_000_000
                if value != 0x800000 and not 0 <= value <= max_fee:
                    raise ValueError(f"fee must be at most {max_fee} or dynamic flag 0x800000")
            if name == "tickSpacing" and not 1 <= value <= 32767:
                raise ValueError("tickSpacing must be between 1 and 32767")
            key[name] = value
    if int(key["currency0"], 16) >= int(key["currency1"], 16):
        raise ValueError("currency0 must sort below currency1")
    return tuple(key[name] for name in fields)


def pool_id_for_key(w3, protocol, pool_key):
    Web3, _ = _web3()
    abi_type = (
        "(address,address,uint24,int24,address)"
        if protocol == "uniswap-v4"
        else "(address,address,address,address,uint24,bytes32)"
    )
    return Web3.keccak(w3.codec.encode([abi_type], [pool_key]))


def _jsonable(value):
    if isinstance(value, (bytes, bytearray)):
        return "0x" + value.hex()
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _rpc(args, Web3):
    chain = ma.get_chain(name=args.chain)
    url = args.rpc_url or os.environ.get("RPC_URL") or chain["rpc"][0]
    w3 = Web3(Web3.HTTPProvider(url, request_kwargs={"timeout": 15}))
    if not w3.is_connected():
        raise ValueError(f"could not connect to {args.chain} RPC")
    observed = w3.eth.chain_id
    if observed != chain["chain_id"]:
        raise ValueError(f"RPC chain ID {observed} != registry chain ID {chain['chain_id']}")
    if args.block is not None and args.block < 0:
        raise ValueError("block must be nonnegative")
    block = args.block if args.block is not None else w3.eth.block_number
    return w3, block


def read_state(args, Web3, HexBytes):
    pool_id = _bytes32(args.pool_id, "pool ID", HexBytes)
    w3, block = _rpc(args, Web3)
    role = "state_view" if args.protocol == "uniswap-v4" else "pool_manager"
    reader = _contract(w3, _record(args.chain, args.protocol, role))
    slot0 = reader.functions.getSlot0(pool_id).call(block_identifier=block)
    if args.protocol != "pancake-infinity-bin" and slot0[0] == 0:
        raise ValueError("pool is not initialized at the selected block")
    result = {
        "protocol": args.protocol, "chain": args.chain, "block": block,
        "poolId": pool_id, "slot0": slot0,
    }
    if args.protocol != "uniswap-v4":
        key = reader.functions.poolIdToPoolKey(pool_id).call(
            block_identifier=block
        )
        if pool_id_for_key(w3, args.protocol, key) != pool_id:
            raise ValueError("pool ID has no matching initialized PoolKey at the selected block")
        result["poolKey"] = key
    if args.protocol != "pancake-infinity-bin":
        result["liquidity"] = reader.functions.getLiquidity(pool_id).call(
            block_identifier=block
        )
    else:
        active_id = slot0[0]
        result["activeBin"] = reader.functions.getBin(pool_id, active_id).call(
            block_identifier=block
        )
    return result


def quote(args, Web3, HexBytes):
    if args.amount_in <= 0 or args.amount_in >= 1 << 128:
        raise ValueError("amount-in must be in uint128 range and positive")
    with args.pool_key_file.open(encoding="utf-8") as source:
        raw_key = json.load(source)
    key = _pool_key(raw_key, args.protocol, Web3, HexBytes)
    hook_data = _hex_bytes(args.hook_data, "hook-data", HexBytes)
    w3, block = _rpc(args, Web3)
    if args.protocol != "uniswap-v4":
        manager = _record(args.chain, args.protocol, "pool_manager")
        if key[3].lower() != manager["address"].lower():
            raise ValueError("PoolKey.poolManager differs from registered pool manager")
    quoter = _contract(w3, _record(args.chain, args.protocol, "quoter"))
    tx = {}
    if args.from_address:
        if not Web3.is_address(args.from_address):
            raise ValueError("from-address must be a 20-byte EVM address")
        tx["from"] = Web3.to_checksum_address(args.from_address)
    amount_out, gas_estimate = quoter.functions.quoteExactInputSingle(
        (key, args.zero_for_one, args.amount_in, hook_data)
    ).call(tx, block_identifier=block)
    return {
        "protocol": args.protocol, "chain": args.chain, "block": block,
        "poolId": pool_id_for_key(w3, args.protocol, key),
        "zeroForOne": args.zero_for_one, "amountIn": args.amount_in,
        "amountOut": amount_out, "gasEstimate": gas_estimate,
    }


def decode_log(args, Web3, HexBytes):
    with args.log_file.open(encoding="utf-8") as source:
        raw = json.load(source)
    if not isinstance(raw, dict) or not isinstance(raw.get("topics"), list):
        raise ValueError("log JSON must be an object with topics array")
    if not Web3.is_address(raw.get("address")):
        raise ValueError("log address must be a 20-byte EVM address")
    log = dict(raw)
    log["topics"] = [_bytes32(topic, "topic", HexBytes) for topic in raw["topics"]]
    log["data"] = _hex_bytes(raw.get("data"), "log data", HexBytes)
    if not log["topics"]:
        raise ValueError("log topics must include event signature")
    for role in ("pool_manager", "position_manager"):
        record = _record(args.chain, args.protocol, role)
        if record["address"].lower() != raw["address"].lower():
            continue
        w3 = Web3()
        contract = _contract(w3, record)
        for item in contract.abi:
            if item["type"] != "event" or item.get("anonymous"):
                continue
            from eth_utils import event_abi_to_log_topic

            if event_abi_to_log_topic(item) != log["topics"][0]:
                continue
            event = getattr(contract.events, item["name"])().process_log(log)
            return {
                "protocol": args.protocol, "chain": args.chain,
                "contractRole": role, "event": event["event"],
                "args": dict(event["args"]),
            }
        raise ValueError("no matching event in registered contract ABI")
    raise ValueError("log address is not a registered manager for this protocol and chain")


def main(argv=None):
    parser = parser_for_cli()
    args = parser.parse_args(argv)
    try:
        Web3, HexBytes = _web3()
    except ValueError as exc:
        parser.error(str(exc))
    from requests.exceptions import RequestException
    from web3.exceptions import Web3Exception

    try:
        operation = {
            "state": read_state, "quote": quote, "decode-log": decode_log
        }[args.command]
        print(json.dumps(_jsonable(operation(args, Web3, HexBytes)), indent=2))
    except (Web3Exception, RequestException) as exc:
        # Provider exceptions may include private RPC credentials or URLs.
        parser.error(f"read-only call failed ({type(exc).__name__}); check the pool, block and RPC")
    except (KeyError, ValueError, OSError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
