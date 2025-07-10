from ast import (
    AST,
    Attribute,
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
    if fun.__name__ in registered_events:
        raise ValueError(f"Event {fun.__name__} already registered.")
    registered_events[fun.__name__] = fun
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
    def visit_Call(self, node: Call) -> Yield | Call:
        self.generic_visit(node)
        func_event = (
            isinstance(node.func, Name) and node.func.id in registered_events
        )
        attr_event = (
            isinstance(node.func, Attribute)
            and node.func.attr in registered_events
        )
        no_outer_yield = not isinstance(
            getattr(node, "_nextrpg_parent", None), Yield
        )
        if (func_event or attr_event) and no_outer_yield:
            return Yield(node)
        return node


registered_events: dict[str, Callable[..., None]] = {}
_add_parent = _AddParent()
_yield = _YieldEvents()
