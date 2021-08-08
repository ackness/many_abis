from setuptools import setup, find_packages

setup(
  name = 'many_abis',
  packages = find_packages(),
  version = '0.0.11',
  license='MIT',
  description = 'A simple way to get different DEXs abis for block chains.',
  author = 'Yong',
  author_email = 'ackness8@gmail.com',
  url = 'https://github.com/ackness/many_abis',
  keywords = ['abi', 'dex', 'block chain', 'bsc', 'eth', 'matic', 'heco', 'kcc', 'pancakeswap', 'mdex', 'quickswap', 'uniswap', 'koffeeswap'],
  install_requires=[
      # 'requests',
      # 'web3',
  ]
)