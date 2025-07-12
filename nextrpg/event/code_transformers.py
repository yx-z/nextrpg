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
    iter_child_nodes,
    unparse,
)
from typing import NoReturn

from nextrpg.event.rpg_event import registered_events


class AddParent(NodeTransformer):
    def visit(self, node: AST) -> AST:
        self.generic_visit(node)
        for child in iter_child_nodes(node):
            child._nextrpg_parent = node
        return node


ADD_PARENT = AddParent()
NEXTRPG_PARENT = "_nextrpg_parent"


class AddYield(NodeTransformer):
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
            getattr(node, NEXTRPG_PARENT, None), Yield
        )
        if (func_event or attr_event) and no_outer_yield:
            return Yield(node)
        return node


ADD_YIELD = AddYield()


class AnnotateSay(NodeTransformer):
    def visit_AnnAssign(self, node: AnnAssign) -> Expr | AnnAssign:
        if node.value is not None:
            return node

        match target_node := node.target:
            case Name():
                target = target_node.id
                arg = []
            case Subscript():
                if isinstance(target_node.value, Name):
                    target = target_node.value.id
                    arg = [target_node.slice]
                else:
                    _raise(node)
            case _:
                _raise(node)

        function = Name("say", Load())
        args = [Name(target, Load()), node.annotation] + arg
        return Expr(Yield(Call(function, args)))


def _raise(node: AnnAssign) -> NoReturn:
    raise ValueError(
        f'Expect var[arg]: "...", where var is player/npc and arg is the ad-hoc config. Got complex expression {unparse(node)}'
    )


ANNOTATE_SAY = AnnotateSay()
