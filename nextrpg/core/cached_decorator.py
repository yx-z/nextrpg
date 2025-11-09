from collections.abc import Callable
from dataclasses import dataclass

from cachetools import LRUCache


@dataclass(frozen=True)
class cached[T, K, **P]:
    size_fun: Callable[[], int]
    key_fun: Callable[P, K | None] = lambda *args, **kwargs: (
        args,
        frozenset(kwargs.items()),
    )

    def __call__[_Type: type](self, cls: _Type) -> _Type:
        cls._nextrpg_instances: LRUCache[K, T] = LRUCache(self.size_fun())

        def new(klass: type[T], *args: P.args, **kwargs: P.kwargs) -> T:
            if klass is not cls:
                return object.__new__(klass)

            if (key := self.key_fun(*args, **kwargs)) is None:
                return object.__new__(klass)

            if (instance := klass._nextrpg_instances.get(key)) is not None:
                return instance

            instance = object.__new__(klass)
            klass._nextrpg_instances[key] = instance
            return instance

        cls.__new__ = new
        return cls
