# Examples

Run these commands from the repository root after installing the project with
Python 3.13 or newer:

```bash
uv sync --locked --dev
uv run python examples/quickstart.py
uv run python examples/inspect_catalog.py --chain base
uv run python examples/inspect_catalog.py --chain xlayer --json
```

`quickstart.py` and `inspect_catalog.py` are deterministic and offline. They
show lazy ABI loading, defensive copies, chain lookup, catalog filtering, and
pinned on-chain evidence without contacting an RPC or Explorer.

## Etherscan V2 lookup

Supply the API key through the environment so it is not stored in source code
or exposed as a command-line argument:

```bash
export ETHERSCAN_API_KEY="your-key"
uv run python examples/etherscan_lookup.py \
  8453 \
  0x2626664c2603336E57B271c5C0b26F421741e481 \
  --output base-uniswap-router.abi.json
```

This example always calls the fixed Etherscan V2 API used by `many-abis`; it
does not accept a custom Explorer URL. A `None` result can mean an invalid key,
an unsupported chain, an unverified contract, rate limiting, or a network
failure.

## web3.py integration

`web3.py` is optional and is intentionally not a runtime dependency of
`many-abis`:

```bash
uv run --with web3 python examples/web3_contract.py
```

The example uses the reviewed official Base RPC from the registry. Set
`RPC_URL` to use a trusted provider instead:

```bash
RPC_URL="https://your-trusted-provider.example" \
  uv run --with web3 python examples/web3_contract.py
```

It reads `factory()` from the registered Uniswap V3 router and compares the
result with the registered factory address. Never treat a successful call, an
ABI provenance record, or a pinned bytecode snapshot as a smart-contract
security audit.
