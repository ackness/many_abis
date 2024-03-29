from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='many_abis',
    # packages=['many_abis'],
    packages=find_packages(where="many_abis"),
    package_dir={'many_abis': 'many_abis'},
    package_data={'': ["assets/*", "tea.yaml"]},
    version='0.1.9',
    license='MIT',
    description='A simple way to get different DEXs abis for block chains.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Yong',
    author_email='ackness8@gmail.com',
    url='https://github.com/ackness/many_abis',
    keywords=['abi', 'dex', 'block chain', 'bsc', 'eth', 'matic', 'heco',
              'kcc', 'pancakeswap', 'mdex', 'quickswap', 'uniswap', 'koffeeswap', "web3"],

    install_requires=[
        "eth_utils",
        "addict"
    ],
    python_requires='>=3.8',

)
