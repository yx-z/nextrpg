"""
Utilities.
"""

from collections.abc import Iterable
from typing import Any, Callable


def partition[T](
    iterable: Iterable[T], /, predicate: Callable[[T], bool]
) -> tuple[list[T], list[T]]:
    """
    Split an iterable into two parts based on a predicate function.

    Args:
        `iterable`: The input iterable to be partitioned

        `predicate`: Function that takes an element and returns `True`/`False`

    Returns:
        `tuple[list[T], list[T]]`: A tuple containing two lists.
            The first list contains elements for which predicate gives `True`.
            The second list contains elements for which predicate gives `False`.
    """
    true = []
    false = []
    for x in iterable:
        if predicate(x):
            true.append(x)
        else:
            false.append(x)
    return true, false


def clone[T](t: T, /, **kwargs: Any) -> T:
    """
    Create a copy of an object with optional attribute overrides.

    Args:
        `t`: The object to clone.

        `**kwargs`: Keyword arguments specifying attributes to override.

    Returns:
        `T`: A new instance of the same type as the input with overrides.
    """

    return type(t)(
        **{k: v for k, v in vars(t).items() if k not in kwargs}, **kwargs
    )
