from enum import Enum
from typing import Any

from pydantic import BaseModel


class EnumModel(Enum):
    def __new__(cls, *args):
        obj = str.__new__(cls)
        obj._value_ = args[0]
        obj.__eq__ = EnumModel.equals
        return obj

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    def equals(obj1, obj2) -> bool:
        return isinstance(obj2, obj1.__class__) and obj1.value == obj2.value


class DictModel(BaseModel):
    @property
    def root(self):
        return getattr(self, '__root__')

    def items(self):
        return self.root.items()

    def __getitem__(self, key: str) -> Any:
        return self.root[key]

    def __setitem__(self, key: str, newvalue: Any):
        self.root[key] = newvalue

    def __contains__(self, key: str):
        return key in self.root

    def __delitem__(self, key: str):
        del self.root[key]

    def dict(self, *args, **kwargs):
        ret = super().dict(*args, **kwargs)
        if "__root__" in ret:
            ret = ret["__root__"]
        return ret
