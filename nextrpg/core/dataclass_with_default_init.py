from collections.abc import Callable
from dataclasses import dataclass, fields
from typing import Any, dataclass_transform


def not_constructor_below() -> Any:
    return None


@dataclass(frozen=True)
class default_init[O, R]:
    init: Callable[[O], R]

    def __call__(self, obj: O) -> R:
        return self.init(obj)


@dataclass_transform(field_descriptors=(not_constructor_below, default_init))
def dataclass_with_default_init[T](
    cls: type[T] | None = None, /, **kwargs: Any
) -> Callable[[type[T]], type[T]] | type[T]:
    if cls is None:
        return lambda c: dataclass_with_default_init(c, **kwargs)

    def post_init(self, *_: Any, **__: Any) -> None:
        if getattr(self, _NEXTRPG_INSTANCE_INIT, None):
            return

        for f in cls_fields:
            if isinstance(attr := getattr(self, f.name, None), default_init):
                object.__setattr__(self, f.name, attr(self))
        object.__setattr__(self, _NEXTRPG_INSTANCE_INIT, True)

    cls.__post_init__ = post_init

    datacls = dataclass(cls, **kwargs)
    cls_fields = fields(datacls)
    return datacls


_NEXTRPG_INSTANCE_INIT = "_nextrpg_instance_init"
