from setuptools import setup, find_packages

setup(
  name = 'many_abis',
  packages = find_packages(),
  version = '0.0.2',
  license='MIT',
  description = 'A simple way to get different DEXs abis for block chains.',
  author = 'Yong',
  author_email = 'ackness8@gmail.com',
  url = 'https://github.com/ackness/many_abis',
  keywords = ['abi', 'dex', 'block chain', 'bsc', 'eth', 'matic', 'heco', 'pancakeswap', 'mdex', 'quickswap'],
  install_requires=[
      'requests',
      'web3',
  ]
)