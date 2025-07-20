"""
Code transformation system for `nextrpg`.

This module provides AST-based code transformers for RPG events in `nextrpg`
games. It includes transformers for adding parent references, yield statements,
and say annotations.

Features:
    - AST node transformation
    - Parent reference tracking
    - Automatic yield insertion
    - Say annotation processing
    - Integration with RPG event system
"""

from ast import (
    AST,
    AnnAssign,
    Attribute,
    Call,
    Expr,
    Load,
    Name,
    NodeTransformer,
    Subscript,
    Yield,
    expr,
    iter_child_nodes,
    unparse,
)
from dataclasses import dataclass
from typing import NamedTuple, NoReturn

from nextrpg.event.rpg_event import registered_events


class _AddParent(NodeTransformer):
    def visit(self, node: AST) -> AST:
        self.generic_visit(node)
        for child in iter_child_nodes(node):
            child._nextrpg_parent = node
        return node


ADD_PARENT = _AddParent()
"""Global instance of the AddParent transformer."""


class _AddYield(NodeTransformer):
    def visit_Call(self, node: Call) -> Yield | Call:
        self.generic_visit(node)
        func_event = isinstance(node.func, Name) and _is_event(node.func.id)
        attr_event = isinstance(node.func, Attribute) and _is_event(
            node.func.attr
        )
        no_outer_yield = not isinstance(
            getattr(node, _NEXTRPG_PARENT, None), Yield
        )
        if (func_event or attr_event) and no_outer_yield:
            return Yield(node)
        return node


ADD_YIELD = _AddYield()
"""Global instance of the AddYield transformer."""


@dataclass(frozen=True)
class AnnotateSay(NodeTransformer):
    """
    AST transformer that processes say annotations.

    This transformer converts type annotations with say strings into actual say
    function calls.
    """

    say_event_name: str

    def visit_AnnAssign(self, node: AnnAssign) -> Expr | AnnAssign:
        """
        Visit and transform an annotated assignment node.

        Converts say annotations like `player: "Hello"` into `player.say("Hello")`
        function calls.

        Arguments:
            node: The annotated assignment node to transform.

        Returns:
            Either a say function call expression or the original annotated
            assignment.

        Raises:
            ValueError: If the annotation format is invalid.
        """
        if node.value is not None:
            return node
        target, arg = _get_target_and_arg(node.target)
        say = Attribute(Name(target, Load()), self.say_event_name, Load())
        return Expr(Call(say, [node.annotation] + arg))


ANNOTATE_SAY = AnnotateSay("say")
"""Global instance of the AnnotateSay transformer."""


_NEXTRPG_PARENT = "_nextrpg_parent"
"""Internal attribute name for parent references."""


def _is_event(name: str) -> bool:
    return name in registered_events


class _TargetAndArg(NamedTuple):
    target: str
    arg: list[expr]


def _get_target_and_arg(node: Name | Attribute | Subscript) -> _TargetAndArg:
    match node:
        case Name():
            return _TargetAndArg(node.id, [])
        case Subscript():
            if isinstance(node.value, Name):
                return _TargetAndArg(node.value.id, [node.slice])
    raise ValueError(
        f'Expect var[arg]: "...", where var is player/npc and arg is the ad-hoc config. Got complex expression {unparse(node)}'
    )
