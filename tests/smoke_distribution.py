"""Smoke-test an installed wheel built from either distribution format."""

from importlib.metadata import distribution, version
from pathlib import PurePosixPath

import many_abis as ma


package = distribution("many-abis")
installed_files = {
    PurePosixPath(str(path)).as_posix() for path in (package.files or ())
}

assert version("many-abis") == ma.__version__
assert ma.loaded_abis() == []
assert len(ma.ALL_ABIS_NAME) > 37
assert all(ma.get_abi(name) for name in ma.ALL_ABIS_NAME)
assert len(ma.all_contract_ids()) > 99
assert ma.get_contract("base:dex:uniswap-v4:state_view")["abi"] == "UNISWAP_V4_STATE_VIEW"
assert ma.get_contract("bsc:dex:pancake-infinity-cl:pool_manager")["abi"]
assert len(ma.all_token_ids()) == 53
assert "many_abis/abis.pyi" in installed_files
assert "many_abis/py.typed" in installed_files
assert any(path.endswith(".dist-info/licenses/LICENSE") for path in installed_files)
assert any(
    path.endswith(".dist-info/licenses/THIRD_PARTY_NOTICES.md")
    for path in installed_files
)
assert any(
    path.endswith(".dist-info/licenses/LICENSES/GPL-2.0.txt")
    for path in installed_files
)
