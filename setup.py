from pathlib import Path

from setuptools import find_packages, setup


ROOT = Path(__file__).resolve().parent
PACKAGE_ROOT = ROOT / "many_abis"
VERSION_NAMESPACE = {}
exec((PACKAGE_ROOT / "version.py").read_text(encoding="utf-8"), VERSION_NAMESPACE)
PACKAGE_DATA = sorted(
    path.relative_to(PACKAGE_ROOT).as_posix()
    for path in (PACKAGE_ROOT / "assets").rglob("*")
    if path.is_file()
)
PACKAGE_DATA.extend(["abis.pyi", "py.typed"])

setup(
    name="many_abis",
    packages=find_packages(),
    package_data={"many_abis": PACKAGE_DATA},
    include_package_data=False,
    version=VERSION_NAMESPACE["__version__"],
    license="MIT",
    license_files=["LICENSE", "THIRD_PARTY_NOTICES.md"],
    description="A simple way to get different DEX ABIs for EVM chains.",
    long_description=(ROOT / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Yong",
    author_email="ackness8@gmail.com",
    url="https://github.com/ackness/many_abis",
    keywords=[
        "abi",
        "dex",
        "blockchain",
        "bsc",
        "eth",
        "base",
        "hyperliquid",
        "monad",
        "robinhood",
        "sonic",
        "unichain",
        "xlayer",
        "pancakeswap",
        "quickswap",
        "uniswap",
        "web3",
    ],
    install_requires=[
        "eth_utils",
        "eth-hash[pycryptodome]>=0.3.1,<1",
        "addict",
        "requests",
        'importlib_resources>=5.10,<7; python_version < "3.9"',
    ],
    python_requires=">=3.8",
)
