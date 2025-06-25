"""
Model definition meta.
"""

from __future__ import annotations

from abc import ABCMeta
from dataclasses import dataclass, field, fields
from typing import Any, Callable, dataclass_transform


@dataclass(frozen=True)
class _Init[S, R]:
    init: Callable[[S], R]


def internal_field[S, R](init: Callable[[S], R]) -> Any:
    """
    Used to mark a field in `Model` as internal.

    Args:
        `init`: Function that takes `self` as argument and returns
            the initial value.

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
    Inherted model classes are an immutable dataclass with `internal_fields`.

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
                object.__setattr__(self, f.name, init.init(self))
