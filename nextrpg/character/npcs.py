from collections.abc import Callable, Generator
from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import Any, Self

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.core import Millisecond
from nextrpg.event.pygame_event import KeyPressDown, KeyboardKey, PygameEvent
from nextrpg.event.rpg_event import transform_event
from nextrpg.logger import FROM_CONFIG, Logger
from nextrpg.model import dataclass_with_instance_init, instance_init
from nextrpg.scene.scene import Scene

logger = Logger("Npcs")


@dataclass_with_instance_init
class NpcOnScreen(CharacterOnScreen):
    """
    In-game NPC interface, where NPC doesn't move.

    Arguments:
        `name`: Name of the NPC.

        `event_spec`: Event specification for player/NPC interactions.
    """

    spec: NpcSpec
    name: str = instance_init(lambda self: self.spec.name)
    character: CharacterDrawing = instance_init(
        lambda self: self.spec.character
    )


@dataclass(frozen=True)
class EventfulScene(Scene):
    """
    EventfulScene allows scenes to continue event execution via coroutine/
        generator.
    """

    _player: PlayerOnScreen
    _npcs: tuple[NpcOnScreen, ...] = field(default_factory=tuple)
    _npc: NpcOnScreen | None = None
    _event: RpgEventGenerator | None = None
    _event_result: Any = None

    @cached_property
    def npcs(self) -> dict[str, NpcOnScreen]:
        return {n.name: n for n in self._npcs}

    def event(self, event: PygameEvent) -> Scene:
        if (
            not self._npc
            and isinstance(event, KeyPressDown)
            and event.key is KeyboardKey.CONFIRM
            and (npc := self._collided_npc)
        ):
            logger.debug(t"Collided with {npc.name}", duration=FROM_CONFIG)
            scene = self._trigger(npc)
            generator = scene._npc.spec._generator(
                scene._player, scene._npc, scene._npcs, scene
            )
            return next(generator)(generator, scene)
        return self.event_without_npc_trigger(event)

    def event_without_npc_trigger(self, event: PygameEvent) -> Self:
        return replace(self, _player=self._player.event(event))

    def tick(self, time_delta: Millisecond) -> Scene:
        if self._next_event:
            return self._next_event
        return self.tick_without_event(time_delta)

    def tick_without_event(self, time_delta: Millisecond) -> Self:
        return replace(
            self,
            _player=self._player.tick(time_delta),
            _npcs=tuple(n.tick(time_delta) for n in self._npcs),
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
        return replace(self, _event=event, _event_result=result)

    @cached_property
    def _collided_npc(self) -> NpcOnScreen | None:
        for npc in self._npcs:
            if self._collide(npc):
                return npc
        return None

    def _collide(self, npc: NpcOnScreen) -> bool:
        return npc.draw_on_screen.rectangle.collide(
            self._player.draw_on_screen.rectangle
        )

    def _trigger(self, npc: NpcOnScreen) -> Self:
        triggered_npc = npc.start_event(self._player)
        npcs = tuple(
            triggered_npc if n.name == npc.name else n for n in self._npcs
        )
        return replace(
            self,
            _player=self._player.start_event(triggered_npc),
            _npc=triggered_npc,
            _npcs=npcs,
        )

    @cached_property
    def _next_event(self) -> Scene | None:
        """
        Get the scene for the next event.

        Returns:
            `Scene | None`: The next scene to continue event execution, if any.
        """
        if not self._event:
            return None

        try:
            return self._event.send(self._event_result)(self._event, self)
        except StopIteration:
            return replace(
                self,
                _player=self._player.complete_event,
                _npcs=self._completed_npcs,
                _npc=None,
                _event=None,
                _event_result=None,
            )

    @cached_property
    def _completed_npcs(self) -> tuple[NpcOnScreen, ...]:
        return tuple(n.complete_event for n in self._npcs)


type RpgEventSpecParams = tuple[
    PlayerOnScreen, NpcOnScreen, dict[str, NpcOnScreen]
]

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


@dataclass(frozen=True)
class RpgEventScene(Scene):
    """
    The event scene.

    Arguments:
        `generator`: The generator to continue after the event.

        `scene`: The scene to continue.
    """

    _generator: RpgEventGenerator
    _scene: EventfulScene


@dataclass_with_instance_init
class NpcSpec:
    """
    Base class to define NPC specifications.

    Arguments:
        `name`: Name of the NPC.

        `drawing`: Character drawing for the NPC.

        `event`: Event specification for player/NPC interactions.
    """

    name: str
    character: CharacterDrawing
    event: RpgEventSpec
    _generator: Callable[[*RpgEventSpecParams], RpgEventGenerator] = (
        instance_init(lambda self: self._create_generator)
    )

    @cached_property
    def _create_generator(
        self,
    ) -> Callable[[*RpgEventSpecParams], RpgEventGenerator]:
        def yield_event(
            player: PlayerOnScreen,
            npc: NpcOnScreen,
            npc_dict: dict[str, NpcOnScreen],
            scene: EventfulScene,
        ) -> RpgEventGenerator:
            ctx = self.event.__globals__.copy()
            exec(transform_event(self.event), ctx)
            return ctx[self.event.__name__](player, npc, npc_dict, scene)

        return yield_event
