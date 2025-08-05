from ast import (
    AST,
    AnnAssign,
    Attribute,
    Call,
    Expr,
    ImportFrom,
    Index,
    Load,
    Name,
    NodeTransformer,
    Subscript,
    Yield,
    YieldFrom,
    alias,
    expr,
    iter_child_nodes,
    unparse,
)
from dataclasses import dataclass
from typing import NamedTuple


class _AddParent(NodeTransformer):
    def visit(self, node: AST) -> AST:
        self.generic_visit(node)
        for child in iter_child_nodes(node):
            child._nextrpg_parent = node
        return node


ADD_PARENT = _AddParent()


@dataclass
class _TransformEvent(NodeTransformer):
    def visit_Module(self, node):
        self.generic_visit(node)
        import_node = ImportFrom(
            module="nextrpg",
            names=[alias(name="transform", asname=_NEXTRPG_TRANSFORM)],
        )
        node.body.insert(0, import_node)
        return node

    def visit_Call(self, node):
        if not isinstance(node.func, Name) or not _is_rpg_event(node.func.id):
            return node
        transform_fun = Call(
            Name(_NEXTRPG_TRANSFORM, Load()), [Name(node.func.id, Load())]
        )
        return Call(transform_fun, node.args, node.keywords)


TRANSFORM_EVENT = _TransformEvent()


class _AddYield(NodeTransformer):
    def visit_Call(self, node: Call) -> Yield | YieldFrom | Call:
        self.generic_visit(node)

        if not isinstance(node.func, (Name, Attribute)) or isinstance(
            getattr(node, _NEXTRPG_PARENT, None), (Yield, YieldFrom)
        ):
            return node

        if isinstance(node.func, Name):
            name = node.func.id
        else:
            name = node.func.attr

        if _is_rpg_event(name):
            return YieldFrom(node)
        if _is_rpg_event_scene(name):
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


def _is_rpg_event(name: str) -> bool:
    from nextrpg.event.event_transformer import registered_rpg_events

    return name in registered_rpg_events


def _is_rpg_event_scene(name: str) -> bool:
    from nextrpg.scene.rpg_event.eventful_scene import (
        registered_rpg_event_scenes,
    )

    return name in registered_rpg_event_scenes


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


_NEXTRPG_TRANSFORM = "_nextrpg_transform"
