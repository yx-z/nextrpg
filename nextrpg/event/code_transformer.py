from ast import (
    AST,
    AnnAssign,
    Attribute,
    Call,
    Expr,
    Import,
    Index,
    Load,
    Name,
    NodeTransformer,
    Subscript,
    Tuple,
    Yield,
    YieldFrom,
    alias,
    expr,
    iter_child_nodes,
    unparse,
)
from dataclasses import dataclass


class _AddParent(NodeTransformer):
    def visit(self, node: AST) -> AST:
        self.generic_visit(node)
        for child in iter_child_nodes(node):
            child._nextrpg_parent = node
        return node


ADD_PARENT = _AddParent()


class _TransformEvent(NodeTransformer):
    def visit_Module(self, node: AST) -> AST:
        self.generic_visit(node)
        import_node = Import([alias("nextrpg")])
        node.body.insert(0, import_node)
        return node

    def visit_Call(self, node: AST) -> AST:
        if not isinstance(node.func, Name) or not _is_rpg_event(node.func.id):
            return node
        args = [Name(node.func.id)]
        transform = Attribute(Name("nextrpg"), "transform_event")
        transform_fun = Call(transform, args)
        return Call(transform_fun, node.args, node.keywords)


TRANSFORM_RPG_EVENT = _TransformEvent()


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
        target_and_args = _get_target_and_arg(node.target)
        args = target_and_args.args
        if len(args) == 1 and not isinstance(args[0], Tuple):
            args = [Tuple(elts=[args[0]], ctx=Load())]
        say = Attribute(Name(target_and_args.target), self.say_event_name)
        return Expr(Call(say, [node.annotation] + args))


ANNOTATE_SAY = AnnotateSay("say")

_NEXTRPG_PARENT = "_nextrpg_parent"


def _is_rpg_event(name: str) -> bool:
    from nextrpg.event.event_transformer import registered_rpg_events

    return name in registered_rpg_events


def _is_rpg_event_scene(name: str) -> bool:
    from nextrpg.event.event_scene import (
        registered_rpg_event_scenes,
    )

    return name in registered_rpg_event_scenes


@dataclass(frozen=True)
class _TargetAndArg:
    target: str
    args: list[expr]


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
