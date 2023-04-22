import json
import os
import glob
from types import SimpleNamespace

root_path = f"{os.path.dirname(os.path.abspath(__file__))}/assets"


def _load_json_file(fp):
    with open(fp) as f:
        abi = json.load(f)
    return abi


def load_abi(name: str):
    with open(os.path.abspath(os.path.join(root_path, f'{name}.abi'))) as f:
        abi = json.load(f)
    return abi


def load_all_abis():
    all_abis_fp = list(glob.iglob(f"{root_path}/**/*.abi", recursive=True))
    return {f'{p[len(root_path):][:-4]}': _load_json_file(p) for p in all_abis_fp}


def load_chains():
    fp = os.path.join(root_path, "utils", "chains.json")
    return _load_json_file(fp)


def print_all_dex():
    from .chains import CHAINS
    for name, chain in CHAINS.items():
        print(f"- {name}:")
        for j, (d_name, dex) in enumerate(chain.dex.items()):
            print(f"  - [{j + 1}] [{dex.name}]({dex.website})")


def supported_abis():
    from .abis import ALL_ABIS_NAME
    # print(ALL_ABIS_NAME)
    return ALL_ABIS_NAME
