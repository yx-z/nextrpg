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
from typing import Any, dataclass_transform


def not_constructor_below() -> Any:
    """
    Sentinel value for marking fields below are not constructor arguments.

    However fields below can still be public member if not prefixed with `_`.

    Returns:
        `Any`: No real return value.
    """
    return field()


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


@dataclass_transform(
    frozen_default=True,
    field_descriptors=(not_constructor_below, instance_init),
)
def dataclass_with_instance_init[T](
    cls: type[T] | None = None, /, **kwargs: Any
) -> Callable[[type[T]], type[T]] | type[T]:
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
    if cls is None:
        return lambda c: dataclass_with_instance_init(c, **kwargs)

    def post_init(self) -> None:
        if getattr(self, _NEXTRPG_INSTANCE_INIT, None):
            return

        for f in fields(self):
            if isinstance(attr := getattr(self, f.name, None), _Init):
                object.__setattr__(self, f.name, attr.init(self))
        object.__setattr__(self, _NEXTRPG_INSTANCE_INIT, True)

    cls.__post_init__ = post_init

    return dataclass(cls, **{"frozen": True} | kwargs)


_NEXTRPG_INSTANCE_INIT = "_nextrpg_instance_init"


@dataclass(frozen=True)
class _Init:
    init: Callable[[Any], Any]
