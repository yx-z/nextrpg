from ast import (
    AST,
    Expr,
    Attribute,
    Call,
    Name,
    Yield,
    AnnAssign,
    Load,
    NodeTransformer,
    iter_child_nodes,
)

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
        if node.value is None:
            target = Name(node.target.id, Load())
            say = Call(Name("say", Load()), [target, node.annotation])
            return Expr(Yield(say))
        return node


ANNOTATE_SAY = AnnotateSay()
