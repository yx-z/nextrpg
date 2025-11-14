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
class _Default[O, R]:
    init: Callable[[O], R]

    def __call__(self, obj: O) -> R:
        return self.init(obj)


def default(fun: Callable[..., Any]) -> Any:
    return _Default(fun)


@overload
def dataclass_with_default[Type: type](
    **kwargs: Any,
) -> Callable[[Type], Type]: ...


@overload
@dataclass_transform(
    field_descriptors=(field, Field, private_init_below, default)
)
def dataclass_with_default[Type: type](cls: Type) -> Type: ...


@dataclass_transform(
    field_descriptors=(field, Field, private_init_below, default)
)
def dataclass_with_default[Type: type](
    cls: Type | None = None, /, **kwargs: Any
) -> Callable[[Type], Type] | Type:
    if cls is None:
        return lambda c: dataclass_with_default(c, **kwargs)

    orig_post_init = getattr(cls, "__post_init__", None)

    def post_init(self, *_: Any, **__: Any) -> None:
        for f in fields(self):
            if isinstance(attr := getattr(self, f.name, None), _Default):
                value = attr(self)
                object.__setattr__(self, f.name, value)
        if orig_post_init:
            orig_post_init(self)

    def getattribute(self, name: str) -> Any:
        if isinstance(value := object.__getattribute__(self, name), _Default):
            res = value(self)
            object.__setattr__(self, name, res)
            return res
        return value

    cls.__post_init__ = post_init
    cls.__getattribute__ = getattribute
    return dataclass(cls, **kwargs)
