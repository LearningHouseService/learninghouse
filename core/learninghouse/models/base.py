import json
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


class EnumModel(Enum):
    def __new__(cls, *args):
        obj = str.__new__(cls)
        obj._value_ = args[0]
        obj.__eq__ = EnumModel.equals
        return obj

    def __str__(self) -> str:
        return str(self._value_)

    def __repr__(self) -> str:
        return str(self._value_)

    @staticmethod
    def equals(obj1, obj2) -> bool:
        return isinstance(obj2, obj1.__class__) and obj1.value == obj2.value

    @classmethod
    def from_string(cls, value: str):
        for item in cls.__members__.values():
            if item.value == value:
                return item
        raise ValueError(f'No enum value {value} found.')


class LHBaseModel(BaseModel):

    def to_json(self, indent: Optional[int] = None) -> str:
        return json.dumps(jsonable_encoder(self), indent=indent)

    def write_to_file(self, filename: str, indent: Optional[int] = None) -> None:
        with open(filename, 'w', encoding="utf-8") as file_pointer:
            file_pointer.write(self.to_json(indent=indent))


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

    def to_json(self, indent: Optional[int] = None):
        return json.dumps(jsonable_encoder(self.dict()), indent=indent)
