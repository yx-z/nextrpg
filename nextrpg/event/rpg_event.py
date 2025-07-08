from ast import (
    AST,
    Call,
    Name,
    NodeTransformer,
    Yield,
    fix_missing_locations,
    iter_child_nodes,
    parse,
)
from collections.abc import Callable
from inspect import getsource
from textwrap import dedent
from types import CodeType


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


def transform_event[R, **P](fun: Callable[P, R]) -> CodeType:
    src = dedent(getsource(fun))
    tree = _yield.visit(_add_parent.visit(parse(src)))
    return compile(fix_missing_locations(tree), "<rpg_event>", "exec")


class _AddParent(NodeTransformer):
    def visit(self, node: AST) -> AST:
        self.generic_visit(node)
        for child in iter_child_nodes(node):
            child._nextrpg_parent = node
        return node


class _YieldEvents(NodeTransformer):
    def visit_Call(self, node: Call) -> Call:
        self.generic_visit(node)
        return (
            Yield(node)
            if isinstance(node.func, Name)
            and node.func.id in _events
            and (parent := getattr(node, "_nextrpg_parent", None))
            and not isinstance(parent, Yield)
            else node
        )


_events: set[str] = set()
_add_parent = _AddParent()
_yield = _YieldEvents()
