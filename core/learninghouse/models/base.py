from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class EnumModel(Enum):
    def __new__(cls, *args):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __str__(self) -> str:
        return str(self._value_)

    def __repr__(self) -> str:
        return str(self._value_)

    def __eq__(self, obj) -> bool:
        return isinstance(obj, self.__class__) and self.value == obj.value

    @classmethod
    def from_string(cls, value: str):
        for item in cls.__members__.values():
            if item.value == value:
                return item
        raise ValueError(f'No enum value {value} found.')


class LHBaseModel(BaseModel):

    def write_to_file(self, filename: str, indent: Optional[int] = None) -> None:
        with open(filename, 'w', encoding="utf-8") as file_pointer:
            file_pointer.write(self.json(indent=indent))

    class Config:
        # pylint: disable=too-few-public-methods
        json_encoders = {
            EnumModel: str
        }


class ListModel(LHBaseModel):
    @property
    def root(self) -> List[Any]:
        return getattr(self, '__root__')

    def __getitem__(self, key: int) -> Any:
        return self.root[key]

    def __setitem__(self, key: int, newvalue: Any):
        self.root[key] = newvalue

    def __delitem__(self, key: int):
        del self.root[key]

    def __str__(self) -> str:
        return str(self.root)

    def __contains__(self, value: Any) -> bool:
        return value in self.root

    def __iter__(self):
        return iter(self.root)

    def insert(self, key: int, newvalue: Any):
        self.root.insert(key, newvalue)

    def append(self, newvalue: Any):
        self.root.append(newvalue)


class DictModel(LHBaseModel):
    @property
    def root(self) -> Dict[str, Any]:
        return getattr(self, '__root__')

    def items(self):
        return self.root.items()

    def keys(self):
        return self.root.keys()

    def values(self):
        return self.root.values()

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
