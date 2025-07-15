from collections.abc import Callable, Generator
from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import Any, Self

from nextrpg.character_on_screen import (
    CharacterOnScreen,
    CharacterSpec,
)
from nextrpg.player_on_screen import PlayerOnScreen
from nextrpg.global_config import config
from nextrpg.core import Millisecond, PixelPerMillisecond
from nextrpg.event_as_attr import EventAsAttr
from nextrpg.pygame_event import KeyPressDown, KeyboardKey, PygameEvent
from nextrpg.event_transformer import transform_and_compile
from nextrpg.logger import Logger
from nextrpg.model import (
    dataclass_with_instance_init,
    instance_init,
    export,
)
from nextrpg.scene import Scene

logger = Logger("Npcs")

__all__ = [
    "RpgEventSpecParams",
    "RpgEventSpec",
    "RpgEventGenerator",
    "RpgEventCallable",
]
type RpgEventSpecParams = tuple[PlayerOnScreen, NpcOnScreen, EventfulScene]

type RpgEventSpec = Callable[[*RpgEventSpecParams], None]
"""
Abstract protocol to define Rpg Event for player/NPC interactions.
"""

type RpgEventGenerator = Generator[RpgEventCallable, Any, None]
"""
The event generator type that can be used to yield an event.
"""

type RpgEventCallable = Callable[
    [RpgEventGenerator, EventfulScene], RpgEventScene
]
"""
The event callable type that can be used to generate a scene for certain event.
"""


@export
@dataclass_with_instance_init
class NpcOnScreen(CharacterOnScreen):
    """
    In-game NPC interface, where NPC doesn't move.

    Arguments:
        `name`: Name of the NPC.

        `event_spec`: Event specification for player/NPC interactions.
    """

    spec: NpcSpec
    generator: Callable[[*RpgEventSpecParams], RpgEventGenerator] = (
        instance_init(lambda self: self.spec.generator)
    )


@export
@dataclass(frozen=True)
class EventfulScene(Scene, EventAsAttr):
    """
    EventfulScene allows scenes to continue event execution via coroutine/
        generator.
    """

    player: PlayerOnScreen
    npcs: tuple[NpcOnScreen, ...] = field(default_factory=tuple)
    npc: NpcOnScreen | None = None
    _event_generator: RpgEventGenerator | None = None
    _event_result: Any = None

    @cached_property
    def npc_dict(self) -> dict[str, NpcOnScreen]:
        return {n.spec.object_name: n for n in self.npcs}

    def event(self, event: PygameEvent) -> Scene:
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
        return replace(self, player=self.player.event(event))

    def tick(self, time_delta: Millisecond) -> Scene:
        if self._next_event:
            return self._next_event
        return self.tick_without_event(time_delta)

    def tick_without_event(self, time_delta: Millisecond) -> Self:
        return replace(
            self,
            player=self.player.tick(time_delta),
            npcs=tuple(n.tick(time_delta) for n in self.npcs),
        )

    def send(self, event: RpgEventGenerator, result: Any = None) -> Self:
        """
        Continue event execution and optionally send the result of
        the current event.

        Arguments:
            `event`: The generator to generate the next event.

            `result`: Result of the current event, passing to the generator.

        Returns:
            `Scene`: The scene that shall continue with the next event.
        """
        return replace(self, _event_generator=event, _event_result=result)

    @cached_property
    def _collided_npc(self) -> NpcOnScreen | None:
        for npc in self.npcs:
            if self._collide(npc):
                return npc
        return None

    def _collide(self, npc: NpcOnScreen) -> bool:
        return npc.draw_on_screen.rectangle.collide(
            self.player.draw_on_screen.rectangle
        )

    def _trigger(self, npc: NpcOnScreen) -> Self:
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
        """
        Get the scene for the next event.

        Returns:
            `Scene | None`: The next scene to continue event execution, if any.
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
        return tuple(n.complete_event for n in self.npcs)


@export
@dataclass(frozen=True)
class RpgEventScene(Scene):
    """
    The event scene.

    Arguments:
        `generator`: The generator to continue after the event.

        `scene`: The scene to continue.
    """

    generator: RpgEventGenerator
    scene: EventfulScene


@export
@dataclass_with_instance_init
class NpcSpec(CharacterSpec):
    """
    Base class to define NPC specifications.

    Arguments:
        `name`: Name of the NPC.

        `drawing`: Character drawing for the NPC.

        `event`: Event specification for player/NPC interactions.
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
        def yield_event(*args: Any, **kwargs: Any) -> RpgEventGenerator:
            fun = self.event
            ctx = fun.__globals__ | {
                v: c.cell_contents
                for v, c in zip(fun.__code__.co_freevars, fun.__closure__ or ())
            }
            exec(transform_and_compile(fun), ctx)
            return ctx[fun.__name__](*args, **kwargs)

        return yield_event
