from ast import (
    Name,
    Assign,
    Call,
    Expr,
    NodeTransformer,
    Yield,
)
from collections.abc import Callable
from dataclasses import dataclass


def register_rpg_event[R, **P](fun: Callable[P, R]) -> Callable[P, R]:
    """
    Mark a function as an event handler.

    Arguments:
        `fun`: Function with a unique name that handles
            player/NPC interaction.

    Returns:
        `Callable`: The original function.
    """
    if fun.__name__ in _events:
        raise ValueError(f"Event {fun.__name__} already registered.")
    _events.add(fun.__name__)
    return fun


@dataclass(frozen=True)
class _YieldEvents(NodeTransformer):
    def visit_Call(self, node: Call) -> Call:
        self.generic_visit(node)
        return (
            Yield(node)
            if isinstance(node.func, Name) and node.func.id in _events
            else node
        )


_events: set[str] = set()
_yield = _YieldEvents()
