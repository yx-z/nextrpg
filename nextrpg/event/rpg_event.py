from ast import (
    Assign,
    Call,
    Expr,
    NodeTransformer,
    Yield,
    fix_missing_locations,
    parse,
)
from collections.abc import Callable, Generator
from dataclasses import dataclass
from functools import wraps
from inspect import getsource
from textwrap import dedent
from typing import Callable

from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.scene.scene import Scene


def register_rpg_event[R, **P](fun: Callable[P, R]) -> Callable[P, R]:
    """
    Mark a function as an event handler.

    Arguments:
        `fun`: Function with a unique name that handles
            player/NPC interaction.

    Returns:
        `Callable`: The original function.
    """
    if fun.__name__ in _events:
        raise ValueError(f"Event {fun.__name__} already registered.")
    _events.add(fun.__name__)
    return fun


type RpgEventSpec = Callable[[PlayerOnScreen, NpcOnScreen, Npcs], None]
"""
Abstract protocol to define Rpg Event for player/NPC interactions.
"""

type RpgEventGenerator[T] = Generator[RpgEventCallable, T, None]
"""
The event generator type that can be used to yield an event.
"""

type RpgEventCallable[T] = Callable[[RpgEventGenerator[T], Scene], Scene]
"""
The event callable type that can be used to generate a scene for certain event.
"""


def wrap_spec(
    fun: RpgEventSpec,
) -> Callable[[PlayerOnScreen, NpcOnScreen, Npcs], RpgEventGenerator]:
    """
    Wrap an event spect to a generator/coroutine. Effectively,

    ```python
    def event(player, *args):
        say(player, "Hello!")
        result = choice(player, "Choosing:", "Good.", "Bad.")
        if result == "Good.": ...
    ```

    becomes

    ```python
    def event(player, *args):
        yield say(player, "Hello!")
        result = yield choice(player, "Choosing:", "Good.", "Bad.")
        if result == "Good.": ...
    ```

    to facilitate the execution of the event, while scene is still returned
    inside game loops.

    Arguments:
        `fun`: The event spec to wrap.

    Returns:
        `RpgEventGenerator`: The wrapped event spec.
    """

    @wraps(fun)
    def wraped(
        player: PlayerOnScreen, npc: NpcOnScreen, npcs: Npcs
    ) -> RpgEventGenerator:
        src = dedent(getsource(fun))
        tree = fix_missing_locations(_yield.visit(parse(src)))
        code = compile(tree, "<npcs>", "exec")
        ctx = fun.__globals__
        exec(code, ctx)
        return ctx[fun.__name__](player, npc, npcs)

    return wraped


@dataclass
class _YieldEvents(NodeTransformer):
    def visit_Expr(self, node: Expr) -> Expr:
        return Expr(Yield(node.value)) if self._is_event(node) else node

    def visit_Assign(self, node: Assign) -> Assign:
        return (
            Assign(node.targets, Yield(node.value))
            if self._is_event(node)
            else node
        )

    def _is_event(self, node) -> bool:
        return (
            isinstance(node.value, Call)
            and getattr(node.value.func, "id", None) in _events
        )


_events: set[str] = set()
_yield = _YieldEvents()
