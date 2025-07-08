from collections.abc import Callable, Generator
from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import Any, Self, override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.core import Millisecond
from nextrpg.event.pygame_event import KeyPressDown, KeyboardKey, PygameEvent
from nextrpg.event.rpg_event import transform_event
from nextrpg.logger import FROM_CONFIG, Logger
from nextrpg.model import instance_init, register_instance_init
from nextrpg.scene.scene import Scene

logger = Logger("Npcs")


@register_instance_init
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
    _triggered: bool = False

    def tick(self, time_delta: Millisecond) -> Self:
        return (
            self
            if self._triggered
            else replace(self, character=self.character.idle(time_delta))
        )

    @override
    def trigger(self, character: CharacterOnScreen) -> Self:
        return replace(super().trigger(character), _triggered=True)

    @cached_property
    def _complete(self) -> Self:
        return replace(self, _triggered=False)


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
    def npc_dict(self) -> dict[str, NpcOnScreen]:
        return {n.name: n for n in self._npcs}

    def event(self, event: PygameEvent) -> Scene:
        if (
            isinstance(event, KeyPressDown)
            and event.key is KeyboardKey.CONFIRM
            and (npc := self._collided_npc)
        ):
            logger.debug(t"Collided with {npc.name}", duration=FROM_CONFIG)
            scene = self._trigger(npc)
            generator = npc.spec._generator(
                self._player, npc, self.npc_dict, scene
            )
            return next(generator)(generator, scene)
        return replace(self, _player=self._player.event(event))

    def tick(self, time_delta: Millisecond) -> Scene:
        if self._next_event:
            return self._next_event
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
        collide = (n for n in self._npcs if self._collide(n))
        return next(collide, None)

    def _collide(self, npc: NpcOnScreen) -> bool:
        return npc.draw_on_screen.rectangle.collide(
            self._player.draw_on_screen.rectangle
        )

    def _trigger(self, npc: NpcOnScreen) -> Self:
        npcs = tuple(
            n.trigger(self._player) if n.name == npc.name else n
            for n in self._npcs
        )
        return replace(
            self,
            _player=self._player.trigger(npc),
            _npc=npc.trigger(self._player),
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
                _npcs=self._complete,
                _npc=None,
                _event=None,
                _event_result=None,
            )

    @cached_property
    def _complete(self) -> tuple[NpcOnScreen, ...]:
        return tuple(
            n._complete if n.name == self._npc.name else n for n in self._npcs
        )


type RpgEventSpec = Callable[
    [PlayerOnScreen, NpcOnScreen, dict[str, NpcOnScreen], EventfulScene],
    None,
]
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


@dataclass(frozen=True)
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

    @cached_property
    def _generator(self) -> Callable[
        [PlayerOnScreen, NpcOnScreen, dict[str, NpcOnScreen], EventfulScene],
        RpgEventGenerator,
    ]:
        def wrapped(
            player: PlayerOnScreen,
            npc: NpcOnScreen,
            npc_dict: dict[str, NpcOnScreen],
            scene: EventfulScene,
        ) -> RpgEventGenerator:
            ctx = self.event.__globals__.copy()
            exec(transform_event(self.event), ctx)
            return ctx[self.event.__name__](player, npc, npc_dict, scene)

        return wrapped
