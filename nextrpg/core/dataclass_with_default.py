from collections.abc import Callable
from dataclasses import dataclass, fields
from typing import Any, TypeVar, dataclass_transform, overload


def not_constructor_below() -> Any:
    return None


@dataclass(frozen=True)
class default[O, R]:
    init: Callable[[O], R]

    def __call__(self, obj: O) -> R:
        return self.init(obj)


_Type = TypeVar("_Type", bound=type)


@overload
def dataclass_with_default(**kwargs: Any) -> Callable[[_Type], _Type]: ...


@overload
def dataclass_with_default(cls: _Type) -> _Type: ...


@dataclass_transform(field_descriptors=(not_constructor_below, default))
def dataclass_with_default(
    cls: _Type | None = None, /, **kwargs: Any
) -> Callable[[_Type], _Type] | _Type:
    if cls is None:
        return lambda c: dataclass_with_default(c, **kwargs)

    def post_init(self, *_: Any, **__: Any) -> None:
        if getattr(self, _NEXTRPG_INSTANCE_INIT, None):
            return

        for f in cls_fields:
            if isinstance(attr := getattr(self, f.name, None), default):
                object.__setattr__(self, f.name, attr(self))
        object.__setattr__(self, _NEXTRPG_INSTANCE_INIT, True)

    cls.__post_init__ = post_init

    datacls = dataclass(cls, **kwargs)
    cls_fields = fields(datacls)
    return datacls


_NEXTRPG_INSTANCE_INIT = "_nextrpg_instance_init"
