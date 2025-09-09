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

    def post_init(self, *_: Any, **__: Any) -> None:
        if getattr(self, _NEXTRPG_INSTANCE_INIT, None):
            return

        field_to_value = {}
        for f in cls_fields:
            if not isinstance(attr := getattr(self, f.name, None), default):
                continue

            if not (value := field_to_value.get(f.name)):
                value = attr(self)
                field_to_value[f.name] = value
            object.__setattr__(self, f.name, value)
        object.__setattr__(self, _NEXTRPG_INSTANCE_INIT, True)

    cls.__post_init__ = post_init

    datacls = dataclass(cls, **kwargs)
    cls_fields = fields(datacls)
    return datacls


def type_name[T](obj: T | type) -> str:
    if isinstance(obj, type):
        cls = obj
    else:
        cls = type(obj)
    return str(cls)[2:-2].split(".")[-1]


_NEXTRPG_INSTANCE_INIT = "_nextrpg_instance_init"
