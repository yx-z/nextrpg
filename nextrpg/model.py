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


@dataclass_transform(kw_only_default=True, frozen_default=True)
def dataclass_with_instance_init[T](cls: type[T]) -> type[T]:
    """
    Class decorator to allow the use of `instance_init` in dataclasses.

    Arguments:
        `cls`: The class to decorate.

    Returns:
        `type`: The decorated class.
    """

    def post_init(self) -> None:
        if getattr(self, _NEXTRPG_INSTANCE_INIT, None):
            return

        for f in fields(self):
            if isinstance(attr := getattr(self, f.name, None), _Init):
                object.__setattr__(self, f.name, attr.init(self))
        object.__setattr__(self, _NEXTRPG_INSTANCE_INIT, True)

    cls.__post_init__ = post_init
    return dataclass(cls, kw_only=True, frozen=True)


_NEXTRPG_INSTANCE_INIT = "_nextrpg_instance_init"


def _key(*args: Any, **kwargs: Any) -> tuple:
    return args, frozenset(kwargs.items())


@dataclass(frozen=True)
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

            if (instance := klass._instances.get(key)) is not None:
                klass._instances.move_to_end(key)
                return instance

            while klass._instances and len(klass._instances) >= self.size_fun():
                klass._instances.popitem(last=False)

            instance = super(klass, klass).__new__(klass)
            klass._instances[key] = instance
            return instance

        cls.__new__ = __new__
        return cls


@dataclass(frozen=True)
class _Init:
    init: Callable[[Any], Any]
