from collections.abc import Callable
from dataclasses import Field, dataclass, field, fields
from typing import (
    Any,
    dataclass_transform,
    overload,
)


class _PrivateInitType:
    pass


_PRIVATE_INIT = _PrivateInitType()


def private_init_below() -> Any:
    return _PRIVATE_INIT


@dataclass(frozen=True)
class _Default[O, R]:
    init: Callable[[O], R]

    def __call__(self, obj: O) -> R:
        return self.init(obj)


def default(fun: Callable[..., Any]) -> Any:
    return _Default(fun)


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

    def post_init(self, *args: Any, **kwargs: Any) -> None:
        for f in fields(self):
            if isinstance(attr := getattr(self, f.name, None), _Default):
                value = attr(self)
                object.__setattr__(self, f.name, value)
        if orig_post_init:
            orig_post_init(self)

    def getattribute(self, name: str) -> Any:
        # Safety net for default fields that reference another not-yet-resolved
        # default field during __post_init__ (e.g. an earlier field whose lambda
        # reads a later field before that later field's own resolution). After
        # __post_init__ completes, every field has been resolved to a real
        # value, so this check is False on the vast majority of
        # post-construction accesses — it exists for the construction window,
        # not the hot path. `type(...) is _Default` is used instead of isinstance
        # because _Default is never subclassed (default() is its only
        # constructor), making it a cheaper pointer comparison with identical
        # semantics.
        if type(value := object.__getattribute__(self, name)) is _Default:
            res = value(self)
            object.__setattr__(self, name, res)
            return res
        return value

    cls.__post_init__ = post_init
    cls.__getattribute__ = getattribute
    return dataclass(cls, **kwargs)
