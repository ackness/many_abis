import eth_utils
from typing import Any
from types import SimpleNamespace


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

    def __parse_address(self):
        for k, v in self.items():
            if eth_utils.is_address(v):
                self[k] = eth_utils.to_checksum_address(v)

    __getattr__ = dict.get
    __delattr__ = dict.__delitem__
