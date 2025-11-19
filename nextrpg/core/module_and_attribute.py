from dataclasses import dataclass
from functools import cached_property
from importlib import import_module
from typing import Self


@dataclass(frozen=True)
class ModuleAndAttribute[T]:
    module: str
    attribute: str

    @cached_property
    def qualname(self) -> str:
        return ".".join((self.module, self.attribute))

    @cached_property
    def save_data(self) -> tuple[str, str]:
        return self.module, self.attribute

    @classmethod
    def load_from_save(cls, data: list[str]) -> Self:
        assert (
            len(data) == 2
        ), f"ModuleAndAttribute only takes [module, attribute]. Got {data}."
        return cls(data[0], data[1])

    @cached_property
    def imported(self) -> T:
        module = import_module(self.module)
        return getattr(module, self.attribute)


def to_module_and_attribute[T](obj: T) -> ModuleAndAttribute[T]:
    return ModuleAndAttribute(obj.__module__, obj.__qualname__)
