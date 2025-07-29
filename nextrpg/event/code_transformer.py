from ast import (
    AST,
    AnnAssign,
    Attribute,
    Call,
    Expr,
    Index,
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
from typing import NamedTuple

from nextrpg.event.rpg_event import registered_events


class _AddParent(NodeTransformer):
    def visit(self, node: AST) -> AST:
        self.generic_visit(node)
        for child in iter_child_nodes(node):
            child._nextrpg_parent = node
        return node


ADD_PARENT = _AddParent()


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


@dataclass(frozen=True)
class AnnotateSay(NodeTransformer):
    say_event_name: str

    def visit_AnnAssign(self, node: AnnAssign) -> Expr | AnnAssign:
        if node.value is not None:
            return node
        target, args = _get_target_and_arg(node.target)
        say = Attribute(Name(target, Load()), self.say_event_name, Load())
        return Expr(Call(say, [node.annotation] + args))


ANNOTATE_SAY = AnnotateSay("say")
"""Global instance of the AnnotateSay transformer."""


_NEXTRPG_PARENT = "_nextrpg_parent"
"""Internal attribute name for parent references."""


def _is_event(name: str) -> bool:
    return name in registered_events


class _TargetAndArg(NamedTuple):
    target: str
    arg: list[expr]


def _get_target_and_arg(target: Name | Attribute | Subscript) -> _TargetAndArg:
    match target:
        case Name():
            return _TargetAndArg(target.id, [])
        case Subscript():
            if isinstance(v := target.value, Name):
                target_id = v.id
            else:
                target_id = v.value.id
            if isinstance(v, Name):
                return _TargetAndArg(target_id, [target.slice])
            if isinstance(target.slice, Index):
                return _TargetAndArg(target_id, target.slice.value.elts)
    raise ValueError(
        f'Expect var[arg1, arg2, ...]: "...", where var is player/npc and arg is the ad-hoc config. Got unexpected expression {unparse(target)}'
    )
