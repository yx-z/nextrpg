"""
Model definition.
"""

from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, field, fields
from typing import Any, dataclass_transform


def instance_init(init: Callable[[Any], Any]) -> Any:
    """
    Used to mark a field for instance initialization.

    Arguments:
        `init`: Function that takes `self` as an argument and returns
            the initial value.

    Returns:
        `Any`: Internal field with the given initialization function.
    """
    return field(repr=False, default_factory=lambda: _Init(init))


@dataclass_transform()
def register_instance_init[T](cls: type[T]) -> type[T]:
    """
    Class decorator to allow the use of `instance_init` in dataclasses.

    Args:
        `cls`: The class to decorate.

    Returns:
        `type`: The decorated class.
    """

    def post_init(self) -> None:
        if getattr(self, _INTERNAL_FIELDS_INITIALIZED, None):
            return

        for f in fields(self):
            if isinstance(attr := getattr(self, f.name), _Init):
                object.__setattr__(self, f.name, attr.init(self))
        object.__setattr__(self, _INTERNAL_FIELDS_INITIALIZED, True)

    cls.__post_init__ = post_init
    return dataclass(cls)


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


@dataclass
class _Init:
    init: Callable[[Any], Any]


_INTERNAL_FIELDS_INITIALIZED = "_INTERNAL_FIELDS_INITIALIZED"
