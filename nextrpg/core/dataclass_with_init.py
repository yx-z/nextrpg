from collections.abc import Callable
from dataclasses import dataclass, field, fields
from typing import Any, dataclass_transform


def not_constructor_below() -> Any:
    return None


def default(init: Callable[[Any], Any]) -> Any:
    return field(repr=False, default_factory=lambda: _Init(init))


@dataclass_transform(field_descriptors=(not_constructor_below, default))
def dataclass_with_init[T](
    cls: type[T] | None = None, /, **kwargs: Any
) -> Callable[[type[T]], type[T]] | type[T]:
    if cls is None:
        return lambda c: dataclass_with_init(c, **kwargs)

    def post_init(self, *_: Any, **__: Any) -> None:
        if getattr(self, _NEXTRPG_INSTANCE_INIT, None):
            return

        for f in cls_fields:
            if isinstance(attr := getattr(self, f.name, None), _Init):
                object.__setattr__(self, f.name, attr(self))
        object.__setattr__(self, _NEXTRPG_INSTANCE_INIT, True)

    cls.__post_init__ = post_init

    datacls = dataclass(cls, **kwargs)
    cls_fields = fields(datacls)
    return datacls


_NEXTRPG_INSTANCE_INIT = "_nextrpg_instance_init"


@dataclass(frozen=True)
class _Init[O, R]:
    init: Callable[[O], R]

    def __call__(self, obj: O) -> R:
        return self.init(obj)
