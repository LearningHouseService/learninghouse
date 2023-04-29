from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, model_serializer, RootModel


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

    def __hash__(self):
        return hash(self.value)

    @classmethod
    def from_string(cls, value: str):
        for item in cls.__members__.values():
            if item.value == value:
                return item
        raise ValueError(f"No enum value {value} found.")

    @model_serializer
    def serialize(self):
        return self.value


class LHBaseModel(BaseModel):
    def write_to_file(self, filename: str, indent: Optional[int] = None) -> None:
        with open(filename, "w", encoding="utf-8") as file_pointer:
            file_pointer.write(self.model_dump_json(indent=indent))

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))


class ListModel(RootModel):
    root: list[Any]

    def append(self, item):
        self.root.append(item)

    def extend(self, items):
        self.root.extend(items)

    def insert(self, index, item):
        self.root.insert(index, item)

    def remove(self, item):
        self.root.remove(item)

    def pop(self, index=-1):
        return self.root.pop(index)

    def clear(self):
        self.root.clear()

    def index(self, item, start=0, end=None):
        return self.root.index(item, start, end)

    def count(self, item):
        return self.root.count(item)

    def sort(self, key=None, reverse=False):
        self.root.sort(key=key, reverse=reverse)

    def reverse(self):
        self.root.reverse()

    def __getitem__(self, index):
        return self.root[index]

    def __setitem__(self, index, value):
        self.root[index] = value

    def __delitem__(self, index):
        del self.root[index]

    def __len__(self):
        return len(self.root)

    def __iter__(self):
        return iter(self.root)

    def __contains__(self, item):
        return item in self.root

    def write_to_file(self, filename: str, indent: Optional[int] = None) -> None:
        with open(filename, "w", encoding="utf-8") as file_pointer:
            file_pointer.write(self.model_dump_json(indent=indent))


class DictModel(RootModel):
    root: dict[str, Any]

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
        if "root" in ret:
            ret = ret["root"]
        return ret

    def write_to_file(self, filename: str, indent: Optional[int] = None) -> None:
        with open(filename, "w", encoding="utf-8") as file_pointer:
            file_pointer.write(self.model_dump_json(indent=indent))
