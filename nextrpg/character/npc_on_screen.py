"""
NPC (Non-Player Character) system for `nextrpg`.

This module provides the core NPC functionality for the `nextrpg` game engine.
It includes classes for managing NPCs on screen, event specifications, and scene
management for player-NPC interactions.

Features:
    - `NpcOnScreen`: In-game NPC interface for stationary NPCs
    - `EventfulScene`: Scene that supports event execution via coroutines/generators
    - `RpgEventScene`: Scene wrapper for RPG events
    - `NpcSpec`: Base class for NPC specifications
    - Type aliases for event specifications and generators
"""

from collections.abc import Callable, Generator
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any

from nextrpg.character.character_on_screen import (
    CharacterOnScreen,
    CharacterSpec,
)
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.core.dimension import PixelPerMillisecond
from nextrpg.core.time import Millisecond
from nextrpg.event.event_transformer import transform_and_compile
from nextrpg.global_config.global_config import config

type RpgEventSpecParams = tuple[PlayerOnScreen, NpcOnScreen, "EventfulScene"]
"""Type alias for RPG event specification parameters.

Contains the player, NPC, and scene context needed for event execution.
"""

type RpgEventSpec = Callable[[*RpgEventSpecParams], None | RpgEventGenerator]
"""Abstract protocol to define RPG events for player/NPC interactions.

This type represents a callable that defines the behavior of an RPG event
when a player interacts with an NPC. The callable receives the player,
NPC, and scene context as parameters.
"""

type RpgEventGenerator = Generator[RpgEventCallable, Any, None]
"""The event generator type that can be used to yield an event.

This type represents a generator that yields event callables and can
receive values during execution. Used for implementing complex
multi-step event sequences.
"""

type RpgEventCallable = Callable[
    [RpgEventGenerator, "EventfulScene"], "RpgEventScene"
]
"""The event callable type that can be used to generate a scene for certain event.

This type represents a callable that takes an event generator and scene,
and returns a new scene that represents the current event state.
"""


@dataclass(frozen=True, kw_only=True)
class NpcSpec(CharacterSpec):
    """Base class to define NPC specifications.

    This class defines the complete specification for an NPC, including
    its appearance, movement behavior, and event interactions.

    Attributes:
        event: Event specification for player/NPC interactions.
        move_speed: Movement speed in pixels per millisecond.
        idle_duration: Duration to stay idle in milliseconds.
        move_duration: Duration to move in milliseconds.
        cyclic_walk: Whether the NPC should walk in cycles.

    Example:
        ```python
        npc_spec = NpcSpec(
            name="Merchant",
            drawing=merchant_drawing,
            event=shop_dialog,
            move_speed=0.05,
            idle_duration=2000,
            move_duration=1000,
            cyclic_walk=True
        )
        ```
    """

    event: RpgEventSpec
    move_speed: PixelPerMillisecond = field(
        default_factory=lambda: config().character.move_speed
    )
    idle_duration: Millisecond = field(
        default_factory=lambda: config().character.idle_duration
    )
    move_duration: Millisecond = field(
        default_factory=lambda: config().character.move_duration
    )
    cyclic_walk: bool = True

    @cached_property
    def generator(self) -> Callable[[*RpgEventSpecParams], RpgEventGenerator]:
        """Create a generator function from the event specification.

        This method transforms the event specification into a generator
        function that can be used for event execution.

        Returns:
            A callable that creates an event generator from the specification.
        """

        fun = self.event
        ctx = fun.__globals__ | {
            v: c.cell_contents
            for v, c in zip(fun.__code__.co_freevars, fun.__closure__ or ())
        }
        exec(transform_and_compile(fun), ctx)
        return ctx[fun.__name__]


@dataclass(frozen=True, kw_only=True)
class NpcOnScreen(CharacterOnScreen):
    """In-game NPC interface for stationary NPCs.

    This class represents an NPC that doesn't move on screen. It provides
    the interface for player-NPC interactions and event handling.

    Attributes:
        spec: The NPC specification containing drawing and event information.

    Example:
        ```python
        npc_spec = NpcSpec(
            name="Villager",
            drawing=character_drawing,
            event=villager_dialog
        )
        npc = NpcOnScreen(spec=npc_spec)
        ```
    """

    spec: NpcSpec
