"""
Code transformation system for NextRPG.

This module provides AST-based code transformers for RPG events
in NextRPG games. It includes transformers for adding parent
references, yield statements, and say annotations.

The code transformation system features:
- AST node transformation
- Parent reference tracking
- Automatic yield insertion
- Say annotation processing
- Integration with RPG event system

Example:
    ```python
    from nextrpg.code_transformers import ADD_PARENT, ADD_YIELD, ANNOTATE_SAY

    # Apply transformers to AST
    tree = ADD_PARENT.visit(tree)
    tree = ADD_YIELD.visit(tree)
    tree = ANNOTATE_SAY.visit(tree)
    ```
"""

from typing import Any
from ast import (
    AST,
    AnnAssign,
    Attribute,
    Call,
    Expr,
    Load,
    Name,
    expr,
    NodeTransformer,
    Subscript,
    Yield,
    iter_child_nodes,
    unparse,
)
from typing import NamedTuple, NoReturn

from nextrpg.rpg_event import registered_events


class AddParent(NodeTransformer):
    """
    AST transformer that adds parent references to nodes.

    This transformer traverses the AST and adds parent references
    to each node, allowing child nodes to access their parent
    during transformation.

    Example:
        ```python
        from nextrpg.code_transformers import AddParent

        transformer = AddParent()
        tree = transformer.visit(tree)
        ```
    """

    def visit(self, node: AST) -> AST:
        """
        Visit and transform an AST node.

        Adds parent references to all child nodes of the given node.

        Arguments:
            `node`: The AST node to transform.

        Returns:
            `AST`: The transformed node with parent references.
        """
        self.generic_visit(node)
        for child in iter_child_nodes(node):
            child._nextrpg_parent = node
        return node


ADD_PARENT = AddParent()
"""Global instance of the AddParent transformer."""


class AddYield(NodeTransformer):
    """
    AST transformer that adds yield statements to event calls.

    This transformer automatically wraps event function calls
    in yield statements to enable coroutine-based event handling.

    Example:
        ```python
        from nextrpg.code_transformers import AddYield

        transformer = AddYield()
        tree = transformer.visit(tree)
        ```
    """

    def visit_Call(self, node: Call) -> Yield | Call:
        """
        Visit and transform a function call node.

        Wraps registered event calls in yield statements if they
        are not already within a yield statement.

        Arguments:
            `node`: The function call node to transform.

        Returns:
            `Yield | Call`: Either a yield statement wrapping the call
                or the original call node.
        """
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


ADD_YIELD = AddYield()
"""Global instance of the AddYield transformer."""


class AnnotateSay(NodeTransformer):
    """
    AST transformer that processes say annotations.

    This transformer converts type annotations with say strings
    into actual say function calls.

    Example:
        ```python
        from nextrpg.code_transformers import AnnotateSay

        transformer = AnnotateSay()
        tree = transformer.visit(tree)
        ```
    """

    def visit_AnnAssign(self, node: AnnAssign) -> Expr | AnnAssign:
        """
        Visit and transform an annotated assignment node.

        Converts say annotations like `player: "Hello"` into
        `player.say("Hello")` function calls.

        Arguments:
            `node`: The annotated assignment node to transform.

        Returns:
            `Expr | AnnAssign`: Either a say function call expression
                or the original annotated assignment.

        Raises:
            `ValueError`: If the annotation format is invalid.
        """
        if node.value is not None:
            return node
        target, arg = _get_target_and_arg(node.target)
        say = Attribute(Name(target, Load()), "say", Load())
        return Expr(Call(say, [node.annotation] + arg))


ANNOTATE_SAY = AnnotateSay()
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
            _raise_annotate_say(node)
        case _:
            _raise_annotate_say(node)


def _raise_annotate_say(node: Subscript | Attribute) -> NoReturn:
    """
    Raise an error for invalid say annotation format.

    Arguments:
        `node`: The invalid annotated assignment node.

    Raises:
        `ValueError`: Always raised with a descriptive error message.
    """
    raise ValueError(
        f'Expect var[arg]: "...", where var is player/npc and arg is the ad-hoc config. Got complex expression {unparse(node)}'
    )
