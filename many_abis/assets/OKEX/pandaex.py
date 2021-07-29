import json


ROUTER_ABI = json.loads('[{"constant":false,"inputs":[{"indexed":false,"internalType":"address","name":"_factory","type":"address"},{"indexed":false,"internalType":"address","name":"_WETH","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"constant":false,"inputs":[],"name":"WETH","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"payable":false,"stateMutability":"payable","type":"receive"},{"constant":false,"inputs":[{"indexed":false,"internalType":"address","name":"tokenA","type":"address"},{"indexed":false,"internalType":"address","name":"tokenB","type":"address"},{"indexed":false,"internalType":"uint256","name":"amountADesired","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountBDesired","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountAMin","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountBMin","type":"uint256"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"address","name":"token","type":"address"},{"indexed":false,"internalType":"uint256","name":"amountTokenDesired","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"payable":false,"stateMutability":"payable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"address","name":"tokenA","type":"address"},{"indexed":false,"internalType":"address","name":"tokenB","type":"address"},{"indexed":false,"internalType":"uint256","name":"liquidity","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountAMin","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountBMin","type":"uint256"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"address","name":"token","type":"address"},{"indexed":false,"internalType":"uint256","name":"liquidity","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"address","name":"tokenA","type":"address"},{"indexed":false,"internalType":"address","name":"tokenB","type":"address"},{"indexed":false,"internalType":"uint256","name":"liquidity","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountAMin","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountBMin","type":"uint256"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"},{"indexed":false,"internalType":"bool","name":"approveMax","type":"bool"},{"indexed":false,"internalType":"uint8","name":"v","type":"uint8"},{"indexed":false,"internalType":"bytes32","name":"r","type":"bytes32"},{"indexed":false,"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityWithPermit","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"address","name":"token","type":"address"},{"indexed":false,"internalType":"uint256","name":"liquidity","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"},{"indexed":false,"internalType":"bool","name":"approveMax","type":"bool"},{"indexed":false,"internalType":"uint8","name":"v","type":"uint8"},{"indexed":false,"internalType":"bytes32","name":"r","type":"bytes32"},{"indexed":false,"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermit","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"address","name":"token","type":"address"},{"indexed":false,"internalType":"uint256","name":"liquidity","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETHSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"address","name":"token","type":"address"},{"indexed":false,"internalType":"uint256","name":"liquidity","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"},{"indexed":false,"internalType":"bool","name":"approveMax","type":"bool"},{"indexed":false,"internalType":"uint8","name":"v","type":"uint8"},{"indexed":false,"internalType":"bytes32","name":"r","type":"bytes32"},{"indexed":false,"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermitSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"address","name":"tokenA","type":"address"},{"indexed":false,"internalType":"address","name":"tokenB","type":"address"},{"indexed":false,"internalType":"uint256","name":"amountADesired","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountBDesired","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountAMin","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountBMin","type":"uint256"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidityNoFee","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"address","name":"token","type":"address"},{"indexed":false,"internalType":"uint256","name":"amountTokenDesired","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidityETHNoFee","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"payable":false,"stateMutability":"payable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"address","name":"tokenA","type":"address"},{"indexed":false,"internalType":"address","name":"tokenB","type":"address"},{"indexed":false,"internalType":"uint256","name":"liquidity","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountAMin","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountBMin","type":"uint256"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityNoFee","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"address","name":"token","type":"address"},{"indexed":false,"internalType":"uint256","name":"liquidity","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETHNoFee","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"address","name":"tokenA","type":"address"},{"indexed":false,"internalType":"address","name":"tokenB","type":"address"},{"indexed":false,"internalType":"uint256","name":"liquidity","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountAMin","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountBMin","type":"uint256"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"},{"indexed":false,"internalType":"bool","name":"approveMax","type":"bool"},{"indexed":false,"internalType":"uint8","name":"v","type":"uint8"},{"indexed":false,"internalType":"bytes32","name":"r","type":"bytes32"},{"indexed":false,"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityWithPermitNoFee","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"address","name":"token","type":"address"},{"indexed":false,"internalType":"uint256","name":"liquidity","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"},{"indexed":false,"internalType":"bool","name":"approveMax","type":"bool"},{"indexed":false,"internalType":"uint8","name":"v","type":"uint8"},{"indexed":false,"internalType":"bytes32","name":"r","type":"bytes32"},{"indexed":false,"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermitNoFee","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"address","name":"token","type":"address"},{"indexed":false,"internalType":"uint256","name":"liquidity","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETHSupportingFeeOnTransferTokensNoFee","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"address","name":"token","type":"address"},{"indexed":false,"internalType":"uint256","name":"liquidity","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"},{"indexed":false,"internalType":"bool","name":"approveMax","type":"bool"},{"indexed":false,"internalType":"uint8","name":"v","type":"uint8"},{"indexed":false,"internalType":"bytes32","name":"r","type":"bytes32"},{"indexed":false,"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermitSupportingFeeOnTransferTokensNoFee","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"amountIn","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"indexed":false,"internalType":"address[]","name":"path","type":"address[]"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"amountOut","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountInMax","type":"uint256"},{"indexed":false,"internalType":"address[]","name":"path","type":"address[]"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"indexed":false,"internalType":"address[]","name":"path","type":"address[]"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"payable":false,"stateMutability":"payable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"amountOut","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountInMax","type":"uint256"},{"indexed":false,"internalType":"address[]","name":"path","type":"address[]"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"amountIn","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"indexed":false,"internalType":"address[]","name":"path","type":"address[]"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"amountOut","type":"uint256"},{"indexed":false,"internalType":"address[]","name":"path","type":"address[]"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapETHForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"payable":false,"stateMutability":"payable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"amountIn","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"indexed":false,"internalType":"address[]","name":"path","type":"address[]"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokensSupportingFeeOnTransferTokens","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"indexed":false,"internalType":"address[]","name":"path","type":"address[]"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokensSupportingFeeOnTransferTokens","outputs":[],"payable":false,"stateMutability":"payable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"amountIn","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"indexed":false,"internalType":"address[]","name":"path","type":"address[]"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETHSupportingFeeOnTransferTokens","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"amountA","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"reserveA","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"reserveB","type":"uint256"}],"name":"quote","outputs":[{"internalType":"uint256","name":"amountB","type":"uint256"}],"payable":false,"stateMutability":"pure","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"amountIn","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountRatio","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"reserveIn","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountOut","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"payable":false,"stateMutability":"pure","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"amountOut","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amountRatio","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"reserveIn","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountIn","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"payable":false,"stateMutability":"pure","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"amountIn","type":"uint256"},{"indexed":false,"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"amountOut","type":"uint256"},{"indexed":false,"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsIn","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"payable":false,"stateMutability":"view","type":"function"}]')
FACTORY_ABI = json.loads('[{"constant":false,"inputs":[{"indexed":false,"internalType":"address","name":"_feeToSetter","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"constant":false,"inputs":[{"indexed":true,"internalType":"address","name":"token0","type":"address"},{"indexed":true,"internalType":"address","name":"token1","type":"address"},{"indexed":false,"internalType":"address","name":"pair","type":"address"},{"indexed":false,"internalType":"uint256","name":"","type":"uint256"}],"name":"PairCreated","payable":false,"type":"event"},{"constant":true,"inputs":[{"indexed":false,"internalType":"uint256","name":"","type":"uint256"}],"name":"allPairs","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"feeTo","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"feeToSetter","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"indexed":false,"internalType":"address","name":"","type":"address"},{"indexed":false,"internalType":"address","name":"","type":"address"}],"name":"getPair","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"allPairsLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"address","name":"tokenA","type":"address"},{"indexed":false,"internalType":"address","name":"tokenB","type":"address"}],"name":"createPair","outputs":[{"internalType":"address","name":"pair","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"address","name":"_feeTo","type":"address"}],"name":"setFeeTo","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"address","name":"_feeToSetter","type":"address"}],"name":"setFeeToSetter","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"address","name":"pairAdress","type":"address"},{"indexed":false,"internalType":"uint256","name":"mintFeeRatio","type":"uint256"}],"name":"updatemintFeeRatio","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"mintFeeRatio","type":"uint256"}],"name":"massUpdatemintFeeRatio","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"_chargeFeeRatio","type":"uint256"}],"name":"massUpdateChargeFeeRatio","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]')

DEX = {
    'name': 'Pandaswap',
    'router_address': '0x6eC2A127057c13Dff1D04e0ae131a756aa4033d4', 
    'router_abi': ROUTER_ABI,
    'factory_address': '0x328C72A24d63E3d903ba9272B95A23ec919eB7E1', 
    'factory_abi': FACTORY_ABI,
    'website': 'https://app.pandaex.org/',
}
