"""
Event transformation system for NextRPG.

This module provides code transformation functionality for RPG events
in NextRPG games. It includes the `transform_and_compile` function
which applies AST transformers to event functions and compiles them.

The event transformation system features:
- AST-based code transformation
- Configurable transformer pipeline
- Source code compilation
- Integration with event configuration

Example:
    ```python
    from nextrpg.event_transformer import transform_and_compile

    def my_event():
        say("Hello, World!")

    # Transform and compile the event
    compiled_code = transform_and_compile(my_event)
    ```
"""

from ast import fix_missing_locations, parse
from inspect import getsource
from textwrap import dedent
from types import CodeType
from typing import Callable

from nextrpg.global_config import config
from nextrpg.model import export


@export
def transform_and_compile(fun: Callable) -> CodeType:
    """
    Transform and compile an event function.

    This function takes an event function, applies configured AST
    transformers to it, and compiles the transformed code. The
    transformers can modify the AST to add event handling capabilities.

    Arguments:
        `fun`: The event function to transform and compile.

    Returns:
        `CodeType`: The compiled bytecode of the transformed function.

    Example:
        ```python
        from nextrpg.event_transformer import transform_and_compile

        def talk_to_npc():
            say("Hello, how are you?")
            wait(1000)

        # Transform and compile the event
        compiled_code = transform_and_compile(talk_to_npc)
        ```
    """
    src = dedent(getsource(fun))
    tree = parse(src)
    for transformer in config().event.transformers:
        tree = transformer.visit(tree)
    return compile(fix_missing_locations(tree), f"<{__file__}>", "exec")
