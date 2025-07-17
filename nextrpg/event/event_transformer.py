"""
Event transformation system for `nextrpg`.

This module provides code transformation functionality for RPG events in
`nextrpg` games. It includes the `transform_and_compile` function which applies
AST transformers to event functions and compiles them.

Features:
    - AST-based code transformation
    - Configurable transformer pipeline
    - Source code compilation
    - Integration with event configuration
"""

from ast import fix_missing_locations, parse
from inspect import getsource
from textwrap import dedent
from types import CodeType
from typing import Callable

from nextrpg.global_config.global_config import config


def transform_and_compile(fun: Callable) -> CodeType:
    """
    Transform and compile an event function.

    This function takes an event function, applies configured AST transformers
    to it, and compiles the transformed code. The transformers can modify the
    AST to add event handling capabilities.

    Arguments:
        fun: The event function to transform and compile.

    Returns:
        The compiled bytecode of the transformed function.
    """
    src = dedent(getsource(fun))
    tree = parse(src)
    for transformer in config().event.transformers:
        tree = transformer.visit(tree)
    return compile(fix_missing_locations(tree), f"<{__file__}>", "exec")
