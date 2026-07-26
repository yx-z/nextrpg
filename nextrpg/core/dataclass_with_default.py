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
        # Eagerly resolve every default field by triggering __getattribute__,
        # which resolves any _Default value on access. This materializes
        # forward-referencing defaults before the user's __post_init__ runs.
        for f in fields(self):
            getattr(self, f.name, None)
        if orig_post_init:
            orig_post_init(self)

    def getattribute(self, name: str) -> Any:
        # Resolve _Default fields on access. Needed during construction when
        # a default lambda reads a sibling field not yet eagerly resolved by
        # post_init (forward references). After construction, every field is
        # resolved and this is a cheap pointer check that returns False.
        #
        # type() is _Default (not isinstance): _Default is never subclassed,
        # so pointer comparison is equivalent and cheaper.
        #
        # No flag-based fast-path: measured pessimization (~318ns vs ~227ns)
        # — the extra object.__getattribute__ for the flag costs more than
        # the type() check it would skip.
        if type(value := object.__getattribute__(self, name)) is _Default:
            res = value(self)
            object.__setattr__(self, name, res)
            return res
        return value

    cls.__post_init__ = post_init
    cls.__getattribute__ = getattribute
    return dataclass(cls, **kwargs)
