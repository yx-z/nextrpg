from collections import OrderedDict
from dataclasses import dataclass
from collections.abc import Callable


@dataclass(frozen=True)
class cached[T, K, **P]:
    """
    Class decorator that caches instances of `T` by a key function.

    This decorator provides automatic caching for class instances based
    on a key function. It's useful for creating singleton-like behavior
    or reducing memory usage for frequently created objects.

    Arguments:
        `size_fun`: Function that returns the maximum size of the cache.

        `key_fun`: Function that takes the same arguments as the class
            and returns a cache key. Defaults to a function that takes
            all args and kwargs.

    Example:
        ```python
        from nextrpg.model import cached

        @cached(size_fun=lambda: 100, key_fun=lambda x, y: (x, y))
        class ExpensiveObject:
            def __init__(self, x: int, y: int):
                self.x = x
                self.y = y
        ```
    """

    size_fun: Callable[[], int]
    key_fun: Callable[P, K | None] = lambda *args, **kwargs: (
        args,
        frozenset(kwargs.items()),
    )

    def __call__(self, cls: type[T]) -> type[T]:
        """
        Apply the caching decorator to the class.

        Sets up the caching mechanism by overriding the `__new__` method
        to check the cache before creating new instances.

        Arguments:
            `cls`: The class to apply caching to.

        Returns:
            `type[T]`: The modified class with caching behavior.
        """
        cls._nextrpg_instances = OrderedDict[K, T]()

        def new(klass: type[T], *args: P.args, **kwargs: P.kwargs) -> T:
            if klass is not cls:
                return object.__new__(klass)

            if (key := self.key_fun(*args, **kwargs)) is None:
                return super(klass, klass).__new__(klass)

            if (instance := klass._nextrpg_instances.get(key)) is not None:
                klass._nextrpg_instances.move_to_end(key)
                return instance

            while (
                klass._nextrpg_instances
                and len(klass._nextrpg_instances) >= self.size_fun()
            ):
                klass._nextrpg_instances.popitem(last=False)

            instance = super(klass, klass).__new__(klass)
            klass._nextrpg_instances[key] = instance
            return instance

        cls.__new__ = new
        return cls
