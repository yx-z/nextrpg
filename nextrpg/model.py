"""
Model utilities and decorators for `nextrpg`.

This module provides utility functions and decorators for creating dataclasses
with instance initialization capabilities and caching mechanisms. These
utilities are used throughout the `nextrpg` framework to create efficient,
immutable data structures.

Features:
    - `export`: Decorator for marking public API elements
    - `instance_init`: Function to mark fields for instance initialization
    - `dataclass_with_instance_init`: Decorator for dataclasses with instance init
    - `cached`: Decorator for creating cached class instances
"""

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
def not_constructor_below() -> Any:
    """
    Sentinel value for marking fields below are not constructor arguments.

    However fields below can still be public member if not prefixed with `_`.

    Returns:
        `Any`: No real return value.
    """
    return field()


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
