from ast import Assign, Call, Expr, NodeTransformer, Yield
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
    if (name := fun.__name__) in _events:
        raise ValueError(f"Event {name} already registered.")
    _events.add(name)
    return fun


@dataclass
class _YieldEvents(NodeTransformer):
    def visit_Expr(self, node: Expr) -> Expr:
        return Expr(Yield(node.value)) if self._is_event(node) else node

    def visit_Assign(self, node: Assign) -> Assign:
        return (
            Assign(node.targets, Yield(node.value))
            if self._is_event(node)
            else node
        )

    def _is_event(self, node) -> bool:
        return (
            isinstance(v := node.value, Call)
            and getattr(v.func, "id", None) in _events
        )


_events: set[str] = set()
_yield = _YieldEvents()
