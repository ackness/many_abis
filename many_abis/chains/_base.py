from typing import Any
from web3 import Web3
from ._assets import *


class AttributeDict(dict):
    """
    A dictionary that can get attribute (x.y) access, including nested dicts.
    """

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__parse_address()

    def __setattr__(self, __name: str, __value: Any) -> None:
        if type(__value) == dict:
            __value = AttributeDict(__value)
            for __key in __value:
                __value.__setattr__(__key, __value[__key])
        self.__setitem__(__name, __value)

    def __parse_address(self, ):
        for k, v in self.items():
            if bool(Web3.isAddress(v)):
                self[k] = Web3.toChecksumAddress(v)

    __getattr__ = dict.get
    __delattr__ = dict.__delitem__


class BaseWETH(AttributeDict):
    def __init__(
            self,
            name: str = None, symbol: str = None,
            address: str = None, abi: dict = WETH_ABI
    ):
        super().__init__(name=name, symbol=symbol, address=address, abi=abi)


class BaseCoin(AttributeDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BaseChart(AttributeDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BaseRPC(AttributeDict):
    def __init__(self, *args, **kwargs):
        self.all = None
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"All rpcs: {self.all}"


class BaseDEX(AttributeDict):
    def __init__(
            self,
            name: str = None,
            router_address: str = None, router_abi: dict = UNISWAP_V2_ROUTER_ABI,
            factory_address: str = None, factory_abi: dict = UNISWAP_V2_FACTORY_ABI,
            lp_abi: dict = UNISWAP_V2_PAIR_ABI,
            website: str = None,
    ):
        super().__init__(
            name=name,
            router_address=router_address,
            router_abi=router_abi,
            factory_address=factory_address,
            factory_abi=factory_abi,
            lp_abi=lp_abi,
            website=website,
        )

    def __repr__(self):
        return f'DEX Name: {self.name}, Website: {self.website}, Router: {self.router_address}, ' \
               f'Factory: {self.factory_address}'


class BaseChain(AttributeDict):
    def __init__(
            self,
            name: str = None, explorer: str = None,
            weth: BaseWETH = None, coins: BaseCoin = None,
            charts: BaseChart = None, rpcs: BaseRPC = None,
            chain_id: int = 0, dex: AttributeDict = None,
    ):
        super().__init__(
            name=name,
            explorer=explorer,
            weth=weth,
            coins=coins,
            charts=charts,
            rpcs=rpcs,
            chain_id=chain_id,
            dex=dex,
        )

    def __repr__(self):
        return f'Chain Name: {self.name}, Explorer: {self.explorer}, DEX: {self.dex.keys()}'
