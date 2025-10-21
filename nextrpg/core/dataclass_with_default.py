from collections.abc import Callable
from dataclasses import Field, dataclass, field, fields
from typing import (
    Any,
    dataclass_transform,
    overload,
)


def private_init_below() -> Any:
    return None


@dataclass(frozen=True)
class default[O, R]:
    init: Callable[[O], R]

    def __call__(self, obj: O) -> R:
        return self.init(obj)


@overload
def dataclass_with_default[T](
    **kwargs: Any,
) -> Callable[[type[T]], type[T]]: ...


@overload
@dataclass_transform(
    field_descriptors=(field, Field, private_init_below, default)
)
def dataclass_with_default[T](cls: type[T]) -> type[T]: ...


@dataclass_transform(
    field_descriptors=(field, Field, private_init_below, default)
)
def dataclass_with_default[T](
    cls: type[T] | None = None, /, **kwargs: Any
) -> Callable[[type[T]], type[T]] | type[T]:
    if cls is None:
        return lambda c: dataclass_with_default(c, **kwargs)

    orig_post_init = getattr(cls, "__post_init__", None)

    def post_init(self, *_: Any, **__: Any) -> None:
        for f in fields(self):
            if isinstance(attr := getattr(self, f.name, None), default):
                value = attr(self)
                object.__setattr__(self, f.name, value)
        if orig_post_init:
            orig_post_init(self)

    def getattribute(self, name: str) -> Any:
        if isinstance(value := object.__getattribute__(self, name), default):
            res = value(self)
            object.__setattr__(self, name, res)
            return res
        return value

    cls.__post_init__ = post_init
    cls.__getattribute__ = getattribute
    return dataclass(cls, **kwargs)


def type_name(obj: Any | type) -> str:
    if isinstance(obj, type):
        cls = obj
    else:
        cls = type(obj)
    return cls.__name__
