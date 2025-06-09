"""
Utilities.
"""

from collections.abc import Iterable
from typing import Callable


def assert_not_none[T](x: T | None, /) -> T:
    """
    Assert that the provided argument is not `None` and returns it.

    Args:
        `x`: The value to be checked.

    Returns:
        The same value as provided in the argument, but never `None`. The result
        retains the type of the input value.

    Raises:
        `AssertionError`: If the provided argument is None.
    """
    assert x is not None
    return x


def partition[T](
    iterable: Iterable[T], /, predicate: Callable[[T], bool]
) -> tuple[list[T], list[T]]:
    """
    Split an iterable into two parts based on a predicate function.

    Args:
        `iterable`: The input iterable to be partitioned.

        `predicate`: Function that takes an element and returns `True`/`False`.
    Returns:
        `tuple[list[T], list[T]]`: A tuple containing two lists -
            The first list contains elements for which predicate returns `True`.
            The second contains elements for which predicate returns `False`.
    """
    true = []
    false = []
    for x in iterable:
        if predicate(x):
            true.append(x)
        else:
            false.append(x)
    return true, false
