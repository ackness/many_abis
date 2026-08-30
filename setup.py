from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='many_abis',
    packages=find_packages(),
    package_data={
        'many_abis': [
            'assets/dex/*/*/*.abi',
            'assets/dex/*/*/*/*.abi',
            'assets/erc/*.abi',
            'assets/tokens/*.abi',
            'assets/utils/chains.json',
        ]
    },
    include_package_data=False,
    version='0.2.0',
    license='MIT',
    description='A simple way to get different DEXs abis for block chains.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Yong',
    author_email='ackness8@gmail.com',
    url='https://github.com/ackness/many_abis',
    keywords=['abi', 'dex', 'block chain', 'bsc', 'eth', 'base', 'hyperliquid',
              'monad', 'robinhood', 'sonic', 'unichain', 'pancakeswap',
              'quickswap', 'uniswap', 'web3'],

    install_requires=[
        "eth_utils",
        "addict",
        "requests",
    ],
    python_requires='>=3.8',

)
