from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class cached[T, K, **P]:
    size_fun: Callable[[], int]
    key_fun: Callable[P, K | None] = lambda *args, **kwargs: (
        args,
        frozenset(kwargs.items()),
    )

    def __call__(self, cls: type[T]) -> type[T]:
        cls._nextrpg_instances = OrderedDict[K, T]()

        def new(klass: type[T], *args: P.args, **kwargs: P.kwargs) -> T:
            if klass is not cls:
                return object.__new__(klass)

            if (key := self.key_fun(*args, **kwargs)) is None:
                return object.__new__(klass)

            if (instance := klass._nextrpg_instances.get(key)) is not None:
                klass._nextrpg_instances.move_to_end(key)
                return instance

            while (
                klass._nextrpg_instances
                and len(klass._nextrpg_instances) >= self.size_fun()
            ):
                klass._nextrpg_instances.popitem(last=False)

            instance = object.__new__(klass)
            klass._nextrpg_instances[key] = instance
            return instance

        cls.__new__ = new
        return cls
