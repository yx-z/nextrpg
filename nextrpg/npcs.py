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
from dataclasses import KW_ONLY, dataclass, field, replace
from functools import cached_property
from typing import Any, Self

from nextrpg.character_on_screen import CharacterOnScreen, CharacterSpec
from nextrpg.core import Millisecond, PixelPerMillisecond
from nextrpg.event_as_attr import EventAsAttr
from nextrpg.event_transformer import transform_and_compile
from nextrpg.global_config import config
from nextrpg.logger import Logger
from nextrpg.model import (
    dataclass_with_instance_init,
    export,
    instance_init,
    not_constructor_below,
)
from nextrpg.player_on_screen import PlayerOnScreen
from nextrpg.pygame_event import KeyboardKey, KeyPressDown, PygameEvent
from nextrpg.scene import Scene

logger = Logger("Npcs")

__all__ = [
    "RpgEventSpecParams",
    "RpgEventSpec",
    "RpgEventGenerator",
    "RpgEventCallable",
]

type RpgEventSpecParams = tuple[PlayerOnScreen, NpcOnScreen, EventfulScene]
"""Type alias for RPG event specification parameters.

Contains the player, NPC, and scene context needed for event execution.
"""

type RpgEventSpec = Callable[[*RpgEventSpecParams], None]
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
    [RpgEventGenerator, EventfulScene], RpgEventScene
]
"""The event callable type that can be used to generate a scene for certain event.

This type represents a callable that takes an event generator and scene,
and returns a new scene that represents the current event state.
"""


@export
@dataclass_with_instance_init
class NpcOnScreen(CharacterOnScreen):
    """In-game NPC interface for stationary NPCs.

    This class represents an NPC that doesn't move on screen. It provides
    the interface for player-NPC interactions and event handling.

    Attributes:
        spec: The NPC specification containing drawing and event information.
        generator: Callable that generates RPG events for this NPC.

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
    _: KW_ONLY = not_constructor_below()
    generator: Callable[[*RpgEventSpecParams], RpgEventGenerator] = (
        instance_init(lambda self: self.spec.generator)
    )


@export
@dataclass(frozen=True)
class EventfulScene(Scene, EventAsAttr):
    """Scene that supports event execution via coroutines/generators.

    This scene type allows for complex event sequences to be executed
    using Python generators. It manages the state of ongoing events
    and provides methods for event continuation and completion.

    Attributes:
        player: The player character on screen.
        npcs: Tuple of NPCs present in the scene.
        npc: Currently active NPC (if any).
        _event_generator: Current event generator being executed.
        _event_result: Result from the previous event step.

    Example:
        ```python
        scene = EventfulScene(
            player=player,
            npcs=(npc1, npc2)
        )

        # Handle events
        scene = scene.event(key_press_event)

        # Update scene over time
        scene = scene.tick(time_delta)
        ```
    """

    player: PlayerOnScreen
    npcs: tuple[NpcOnScreen, ...] = field(default_factory=tuple)
    _: KW_ONLY = not_constructor_below()
    npc: NpcOnScreen | None = None
    _event_generator: RpgEventGenerator | None = None
    _event_result: Any = None

    @cached_property
    def npc_dict(self) -> dict[str, NpcOnScreen]:
        """Get a dictionary mapping NPC names to NPC objects.

        Returns:
            Dictionary with NPC object names as keys and NPC objects as values.
        """
        return {n.spec.object_name: n for n in self.npcs}

    def event(self, event: PygameEvent) -> Scene:
        """Handle pygame events and trigger NPC interactions.

        This method processes pygame events and automatically triggers
        NPC interactions when the player collides with an NPC and
        presses the confirm key.

        Args:
            event: The pygame event to process.

        Returns:
            The updated scene after processing the event.
        """
        if (
            not self.npc
            and isinstance(event, KeyPressDown)
            and event.key is KeyboardKey.CONFIRM
            and (npc := self._collided_npc)
        ):
            logger.debug(t"Collided with {npc.spec.object_name}")
            scene = self._trigger(npc)
            generator = scene.npc.generator(scene.player, scene.npc, scene)
            logger.debug(t"Event {generator.__name__} started.")
            return next(generator)(generator, scene)
        return self.event_without_npc_trigger(event)

    def event_without_npc_trigger(self, event: PygameEvent) -> Self:
        """Handle events without triggering NPC interactions.

        Args:
            event: The pygame event to process.

        Returns:
            Updated scene with only player event processing.
        """
        return replace(self, player=self.player.event(event))

    def tick(self, time_delta: Millisecond) -> Scene:
        """Update the scene state over time.

        This method updates the scene and handles ongoing events.
        If there's a next event to process, it will be executed.

        Args:
            time_delta: Time elapsed since last update in milliseconds.

        Returns:
            Updated scene state.
        """
        if self._next_event:
            return self._next_event
        return self.tick_without_event(time_delta)

    def tick_without_event(self, time_delta: Millisecond) -> Self:
        """Update scene state without processing events.

        Args:
            time_delta: Time elapsed since last update in milliseconds.

        Returns:
            Updated scene with player and NPCs updated.
        """
        return replace(
            self,
            player=self.player.tick(time_delta),
            npcs=tuple(n.tick(time_delta) for n in self.npcs),
        )

    def send(self, event: RpgEventGenerator, result: Any = None) -> Self:
        """Continue event execution and optionally send the result of the current event.

        This method is used to continue the execution of an event generator
        and can pass a result value to the generator.

        Args:
            event: The generator to generate the next event.
            result: Result of the current event, passing to the generator.

        Returns:
            Scene that shall continue with the next event.
        """
        return replace(self, _event_generator=event, _event_result=result)

    @cached_property
    def _collided_npc(self) -> NpcOnScreen | None:
        """Find the NPC that the player is currently colliding with.

        Returns:
            The NPC the player is colliding with, or None if no collision.
        """
        for npc in self.npcs:
            if self._collide(npc):
                return npc
        return None

    def _collide(self, npc: NpcOnScreen) -> bool:
        """Check if the player is colliding with an NPC.

        Args:
            npc: The NPC to check collision with.

        Returns:
            True if the player is colliding with the NPC, False otherwise.
        """
        return npc.draw_on_screen.rectangle.collide(
            self.player.draw_on_screen.rectangle
        )

    def _trigger(self, npc: NpcOnScreen) -> Self:
        """Trigger an event with the specified NPC.

        This method prepares the scene for an NPC interaction by
        setting up the NPC and player in event mode.

        Args:
            npc: The NPC to trigger an event with.

        Returns:
            Updated scene with the NPC event triggered.
        """
        triggered_npc = npc.start_event(self.player)
        npcs = tuple(
            triggered_npc if n.spec.object_name == npc.spec.object_name else n
            for n in self.npcs
        )
        return replace(
            self,
            player=self.player.start_event(triggered_npc),
            npc=triggered_npc,
            npcs=npcs,
        )

    @cached_property
    def _next_event(self) -> Scene | None:
        """Get the scene for the next event.

        This method continues the execution of the current event generator
        and returns the next scene in the event sequence.

        Returns:
            The next scene to continue event execution, or None if no event.
        """
        if not self._event_generator:
            return None

        try:
            create_next_scene = self._event_generator.send(self._event_result)
            return create_next_scene(self._event_generator, self)
        except StopIteration:
            return self._clear_event

    @cached_property
    def _clear_event(self) -> Self:
        """Clear the current event and return to normal scene state.

        This method is called when an event sequence completes and
        returns the scene to its normal state.

        Returns:
            Scene with event state cleared.
        """
        logger.debug(t"Event {self._event_generator.__name__} completed.")
        return replace(
            self,
            player=self.player.complete_event,
            npcs=self._completed_npcs,
            npc=None,
            _event_generator=None,
            _event_result=None,
        )

    @cached_property
    def _completed_npcs(self) -> tuple[NpcOnScreen, ...]:
        """Get NPCs with their events completed.

        Returns:
            Tuple of NPCs with their event states completed.
        """
        return tuple(n.complete_event for n in self.npcs)


@export
@dataclass(frozen=True)
class RpgEventScene(Scene):
    """Scene wrapper for RPG events.

    This class represents a scene that is part of an RPG event sequence.
    It contains the event generator and the underlying scene context.

    Attributes:
        generator: The generator to continue after the event.
        scene: The scene to continue.

    Example:
        ```python
        event_scene = RpgEventScene(
            generator=event_generator,
            scene=base_scene
        )
        ```
    """

    generator: RpgEventGenerator
    scene: EventfulScene


@export
@dataclass_with_instance_init
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

        def yield_event(*args: Any, **kwargs: Any) -> RpgEventGenerator:
            fun = self.event
            ctx = fun.__globals__ | {
                v: c.cell_contents
                for v, c in zip(fun.__code__.co_freevars, fun.__closure__ or ())
            }
            exec(transform_and_compile(fun), ctx)
            return ctx[fun.__name__](*args, **kwargs)

        return yield_event
