"""
Model utilities and decorators for NextRPG.

This module provides utility functions and decorators for creating
dataclasses with instance initialization capabilities and caching
mechanisms. These utilities are used throughout the NextRPG framework
to create efficient, immutable data structures.

The module includes:
- `export`: Decorator for marking public API elements
- `instance_init`: Function to mark fields for instance initialization
- `dataclass_with_instance_init`: Decorator for dataclasses with instance init
- `cached`: Decorator for creating cached class instances

These utilities help create efficient data structures that can be
safely shared and cached across the game framework.

Example:
    ```python
    from nextrpg.model import dataclass_with_instance_init, instance_init, cached

    @dataclass_with_instance_init
    class MyClass:
        value: int
        computed: str = instance_init(lambda self: f"Value: {self.value}")

    @cached(size_fun=lambda: 100)
    class ExpensiveObject:
        def __init__(self, x: int, y: int):
            self.x = x
            self.y = y
    ```
"""

from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, field, fields
from sys import modules
from typing import Any, dataclass_transform


def export[T](o: T) -> T:
    """
    Mark an object as part of the public API.

    This decorator adds the decorated object to the module's `__all__`
    list, making it part of the public API that should be imported
    when using `from module import *`.

    Arguments:
        `o`: The object to mark as exported.

    Returns:
        `T`: The original object, unchanged.

    Example:
        ```python
        from nextrpg.model import export

        @export
        def my_function():
            pass

        @export
        class MyClass:
            pass
        ```
    """
    mod = modules[o.__module__]
    if hasattr(mod, "__all__"):
        if o.__name__ not in mod.__all__:
            mod.__all__.append(o.__name__)
    else:
        mod.__all__ = [o.__name__]
    return o


export = export(export)


@export
def instance_init(init: Callable[[Any], Any]) -> Any:
    """
    Mark a field for instance initialization in dataclasses.

    This function creates a special field that will be initialized
    after the dataclass instance is created, allowing access to
    other instance attributes during initialization.

    Arguments:
        `init`: Function that takes `self` as an argument and returns
            the initial value for the field.

    Returns:
        `Any`: Internal field marker with the given initialization function.

    Example:
        ```python
        from nextrpg.model import dataclass_with_instance_init, instance_init

        @dataclass_with_instance_init
        class MyClass:
            value: int
            computed: str = instance_init(lambda self: f"Value: {self.value}")
        ```
    """
    return field(repr=False, default_factory=lambda: _Init(init))


@export
@dataclass_transform(kw_only_default=True, frozen_default=True)
def dataclass_with_instance_init[T](cls: type[T]) -> type[T]:
    """
    Class decorator to allow the use of `instance_init` in dataclasses.

    This decorator enhances dataclasses with the ability to use
    `instance_init` fields. It automatically handles the post-initialization
    process for fields marked with `instance_init`.

    Arguments:
        `cls`: The class to decorate.

    Returns:
        `type`: The decorated class with instance initialization support.

    Example:
        ```python
        from nextrpg.model import dataclass_with_instance_init, instance_init

        @dataclass_with_instance_init
        class Character:
            name: str
            level: int
            display_name: str = instance_init(
                lambda self: f"{self.name} (Lv.{self.level})"
            )
        ```
    """

    def post_init(self) -> None:
        """
        Post-initialization hook for instance init fields.

        Processes all fields marked with `instance_init` and calls
        their initialization functions with the instance as argument.
        """
        if getattr(self, _NEXTRPG_INSTANCE_INIT, None):
            return

        for f in fields(self):
            if isinstance(attr := getattr(self, f.name, None), _Init):
                object.__setattr__(self, f.name, attr.init(self))
        object.__setattr__(self, _NEXTRPG_INSTANCE_INIT, True)

    cls.__post_init__ = post_init
    return dataclass(cls, kw_only=True, frozen=True)


@export
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
        cls._instances = OrderedDict[K, T]()

        def __new__(klass: type[T], *args: P.args, **kwargs: P.kwargs) -> T:
            """
            Create or retrieve a cached instance.

            Checks the cache for an existing instance with the same key.
            If found, returns the cached instance. Otherwise, creates
            a new instance and adds it to the cache.

            Arguments:
                `*args`: Positional arguments for the class constructor.

                `**kwargs`: Keyword arguments for the class constructor.

            Returns:
                `T`: Either a cached instance or a newly created one.
            """
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


_NEXTRPG_INSTANCE_INIT = "_nextrpg_instance_init"


@dataclass(frozen=True)
class _Init:
    """
    Internal class for instance initialization markers.

    This class is used internally by the `instance_init` function
    to mark fields that should be initialized after the dataclass
    instance is created.

    Arguments:
        `init`: The initialization function to call with the instance.
    """

    init: Callable[[Any], Any]
