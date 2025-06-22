from __future__ import annotations

from typing import Any, Callable

INTERNAL: Any = object()
"""Used to mark fields as internal-only and not exposed to the library user."""


def is_internal_field_initialized(field: Any) -> bool:
    """
    Checks if a field is initialized to a value other than `INTERNAL`.

    Args:
        `field` : The field to check.

    Returns:
        `bool`: `True` if the field is initialized, `False` otherwise.
    """
    return field is not INTERNAL


def initialize_internal_field[**P, R](
    self: Any,
    name: str,
    factory: Callable[P, R],
    *args: P.args,
    **kwargs: P.kwargs,
) -> R | None:
    """
    Used to init `INTERNAL_ONLY` field in `dataclass` instance.

    Args:
        `self`: Object to set.

        `name`: Name of the field.

        `factory`: Factory function to create the value of the field.
            This is a factory to avoid potential side effects when creating
            the field.

        `*args`: Positional arguments to pass to the factory function.

        `**kwargs`: Keyword arguments to pass to the factory function.

    Returns:
        `R` | `None`: The initialized value of the field.
    """
    if is_internal_field_initialized(getattr(self, name)):
        return None
    val = factory(*args, **kwargs)
    object.__setattr__(self, name, val)
    return val
