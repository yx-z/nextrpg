"""
Utilities.
"""

from collections.abc import Iterable
from typing import Callable


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
