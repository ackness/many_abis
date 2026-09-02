from pathlib import Path
import re

from setuptools import find_packages, setup


ROOT = Path(__file__).resolve().parent
PACKAGE_ROOT = ROOT / "many_abis"
VERSION_MATCH = re.fullmatch(
    r'__version__\s*=\s*"([^"]+)"\s*',
    (PACKAGE_ROOT / "version.py").read_text(encoding="utf-8"),
)
if VERSION_MATCH is None:
    raise RuntimeError("many_abis/version.py must contain one literal __version__")
VERSION = VERSION_MATCH.group(1)
PACKAGE_DATA = sorted(
    path.relative_to(PACKAGE_ROOT).as_posix()
    for path in (PACKAGE_ROOT / "assets").rglob("*")
    if path.is_file()
)
PACKAGE_DATA.extend(["abis.pyi", "py.typed"])

setup(
    name="many-abis",
    packages=find_packages(),
    package_data={"many_abis": PACKAGE_DATA},
    include_package_data=False,
    version=VERSION,
    license="MIT",
    license_files=["LICENSE", "THIRD_PARTY_NOTICES.md", "LICENSES/*"],
    description="Verified ABI and EVM chain metadata with pinned provenance.",
    long_description=(ROOT / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Yong",
    url="https://github.com/ackness/many_abis",
    project_urls={
        "Documentation": "https://github.com/ackness/many_abis#readme",
        "Issues": "https://github.com/ackness/many_abis/issues",
        "License and provenance": (
            "https://github.com/ackness/many_abis/blob/main/"
            "THIRD_PARTY_NOTICES.md"
        ),
        "Source": "https://github.com/ackness/many_abis",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
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
        "addict>=2.4,<3",
        "eth-hash[pycryptodome]>=0.8,<1",
        "eth_utils>=6,<7",
        "pycryptodome>=3.23,<4",
        "requests>=2.33,<3",
        "urllib3>=2.7,<3",
    ],
    python_requires=">=3.13",
)
