from many_abis.utils.utils import get_factory_from_router, get_abi_from_address
from many_abis.utils.enum.chain_rpc_enum import CHAIN_RPC_API as rpc
from many_abis.utils.enum.contract_api_enum import CHAIN_CONTRACT_API as contract_api

# get router abi
abi = get_abi_from_address('0x10ED43C718714eb63d5aA57B78B54704E256024E', 'YOUR_API_KEY', chain_api=contract_api.BSC)

# get factory abi
factory_address, factory_abi = get_factory_from_router('0x10ED43C718714eb63d5aA57B78B54704E256024E', 'YOUR_API_KEY',
                                                       chain_api=contract_api.BSC, rpc=rpc.BSC)
