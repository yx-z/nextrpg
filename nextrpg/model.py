"""
Model definition meta.
"""

from __future__ import annotations

from abc import ABCMeta
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, field, fields
from typing import Any, dataclass_transform


@dataclass(frozen=True)
class _Init[S, R]:
    init: Callable[[S], R] | Callable[[], R] | R


def internal_field[S, R](init: Callable[[S], R] | Callable[[], R] | R) -> Any:
    """
    Used to mark a field in `Model` as internal.

    Arguments:
        `init`: Function that takes `self` as an argument and returns
            the initial value, or a callable that takes no arguments,
            or a constant value.

    Returns:
        `Any`: Internal field with the given initialization function.
    """
    return field(repr=False, default=_Init(init))


@dataclass_transform(frozen_default=True)
class _Meta[T](ABCMeta):
    def __new__(cls, *args: Any, **kwargs: Any) -> type:
        klass: type = super().__new__(cls, *args, **kwargs)
        return dataclass(frozen=True)(klass)


class Model(metaclass=_Meta):
    """
    Base class to inherit from for models.
    Inherited model classes are an immutable dataclass with `internal_fields`.

    Example usage:
    ```python
    from dataclasses import field, KW_ONLY
    from nextrpg.model import internal_field, Model

    class MyModel(Model):
        user_input: str
        public_data: str = "public"
        _: KW_ONLY = field()
        _internal_data: str = internal_field(
            lambda self: f"internal {self.public_data}"
        )
    ```
    """

    def __post_init__(self) -> None:
        for f in fields(self):
            if isinstance(init := getattr(self, f.name), _Init):
                if callable(init.init):
                    try:
                        object.__setattr__(self, f.name, init.init())
                    except TypeError:
                        object.__setattr__(self, f.name, init.init(self))
                else:
                    object.__setattr__(self, f.name, init.init)


class cached[T, K, **P](Model):
    """
    Class decorator to cache instances of a class by a certain size
    and a key function.

    Arguments:
        `T`: Type of the class to be cached.

        `K`: Type of the cache key.

        `P`: ParamSpec of the arguments to the class __new__ / constructor.

        `size_fun`: Function that returns the maximum size of the cache.

        `key_fun`: Function that takes the same arguments as the class, to
            be used as the cache key. Defaults to a function that takes all
            args and kwargs.
    """

    size_fun: Callable[[], int]
    key_fun: Callable[P, K | None] = field(
        default=lambda *args, **kwargs: (args, frozenset(kwargs.items()))
    )

    def __call__(self, cls: type[T]) -> type[T]:
        cls._cache = OrderedDict[K, T]()

        def __new__(klass: type[T], *args: P.args, **kwargs: P.kwargs) -> T:
            key = self.key_fun(*args, **kwargs)
            if key is None:
                return super(klass, klass).__new__(klass)

            if key in klass._cache:
                klass._cache.move_to_end(key)
                return klass._cache[key]

            while len(klass._cache) >= self.size_fun():
                klass._cache.popitem(last=False)

            instance = super(klass, klass).__new__(klass)
            klass._cache[key] = instance
            return instance

        cls.__new__ = __new__
        return cls
