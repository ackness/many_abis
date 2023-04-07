from .utils import load_all_abis
from addict import Dict


def all_abis():
    all_abis = load_all_abis()
    names = []
    all_abis_rename = {}
    for k, v in all_abis.items():
        ns = k.split('/')[2:]
        name = '_'.join(ns).upper()
        names.append(name)
        all_abis_rename[name] = v
    return names, Dict(all_abis_rename)


ALL_ABIS_NAME, ABIS = all_abis()
globals().update(ABIS)
