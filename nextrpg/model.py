"""
Model definition meta.
"""

from abc import ABCMeta
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import Field, dataclass, field, fields
from typing import Any, dataclass_transform


def internal_field(init: Callable[[Any], Any] | Callable[[], Any] | Any) -> Any:
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
        return dataclass(frozen=True)(super().__new__(cls, *args, **kwargs))


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
        if getattr(self, _INTERNAL_FIELDS_INITIALIZED, None):
            return

        for f in fields(self):
            self._init_field(f)
        object.__setattr__(self, _INTERNAL_FIELDS_INITIALIZED, True)

    def _init_field(self, f: Field) -> None:
        if not isinstance(attr := getattr(self, f.name), _Init):
            return

        if not callable(init := attr.init):
            self._set_attr(f, init)
            return

        try:
            self._set_attr(f, init())
        except TypeError:
            self._set_attr(f, init(self))

    def _set_attr(self, f: Field, value: Any) -> None:
        object.__setattr__(self, f.name, value)


def _key(*args: Any, **kwargs: Any) -> tuple:
    return args, frozenset(kwargs.items())


@dataclass
class cached[T, K, **P]:
    """
    Class decorator to `T` that caches instances of `T` by a certain size
    and a key function that takes `**P` and returns `K`.

    Arguments:
        `size_fun`: Function that returns the maximum size of the cache.

        `key_fun`: Function that takes the same arguments as the class, to
            be used as the cache key. Defaults to a function that takes all
            args and kwargs.
    """

    size_fun: Callable[[], int]
    key_fun: Callable[P, K | None] = _key

    def __call__(self, cls: type[T]) -> type[T]:
        cls._instances = OrderedDict[K, T]()

        def __new__(klass: type[T], *args: P.args, **kwargs: P.kwargs) -> T:
            if (key := self.key_fun(*args, **kwargs)) is None:
                return super(klass, klass).__new__(klass)

            if key in klass._instances:
                klass._instances.move_to_end(key)
                return klass._instances[key]

            while len(klass._instances) >= self.size_fun():
                klass._instances.popitem(last=False)

            instance = super(klass, klass).__new__(klass)
            klass._instances[key] = instance
            return instance

        cls.__new__ = __new__
        return cls


class _Init(Model):
    init: Callable[[Any], Any] | Callable[[], Any] | Any


_INTERNAL_FIELDS_INITIALIZED = "_INTERNAL_FIELDS_INITIALIZED"
