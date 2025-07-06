from ast import fix_missing_locations, parse
from collections.abc import Callable, Generator
from inspect import getsource
from dataclasses import dataclass, replace
from functools import cached_property, wraps
from textwrap import dedent
from typing import Self

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.core import Millisecond
from nextrpg.event.pygame_event import KeyPressDown, KeyboardKey, PygameEvent
from nextrpg.event.rpg_event import _yield
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
    _generator: RpgEventGenerator = instance_init(
        lambda self: self.spec._generator
    )
    _triggered: bool = False

    def tick(self, time_delta: Millisecond) -> Self:
        return (
            self
            if self._triggered
            else replace(self, character=self.character.idle(time_delta))
        )

    def _trigger(self, player: PlayerOnScreen) -> Self:
        direction = player.character.direction.opposite
        return replace(
            self, character=self.character.turn(direction), _triggered=True
        )

    @cached_property
    def _completed(self) -> Self:
        return replace(self, _triggered=False)


@register_instance_init
class Npcs[T]:
    """
    A collection of NPCs.

    Arguments:
        `list`: List of NPCs.
    """

    list: list[NpcOnScreen]

    def event(
        self,
        event: PygameEvent,
        player: PlayerOnScreen,
        scene: EventfulScene[T],
    ) -> RpgEventScene | None:
        """
        Trigger the NPC event.

        `Arguments`:
            `event`: The pygame event to trigger.

            `player`: The current player.

            `scene`: The current scene.

        Returns:
            `Scene`: The scene after the event is triggered, if any.
        """
        if (
            isinstance(event, KeyPressDown)
            and event.key is KeyboardKey.CONFIRM
            and (npc := self._collided_npc(player))
        ):
            logger.debug(t"Collided with {npc.name}", duration=FROM_CONFIG)
            triggered_scene = scene._trigger(player, npc)
            generator = npc._generator(
                player, triggered_scene, triggered_scene._npcs
            )
            return next(generator)(generator, triggered_scene)
        return None

    def tick(self, time_delta: Millisecond) -> Self:
        """
        Update the npc state for a single game loop.

        Arguments:
            `time_delta`: The elapsed time since the last update.

        Returns:
            `Npcs`: The updated npc state after the step.
        """
        return replace(
            self,
            list=[n.tick(time_delta) for n in self.list],
        )

    def _collided_npc(self, player: PlayerOnScreen) -> NpcOnScreen | None:
        collide = (n for n in self.list if _collide(player, n))
        return next(collide, None)

    def _complete(self, npc: NpcOnScreen) -> Self:
        return replace(
            self,
            list=[n._completed if n.name == npc.name else n for n in self.list],
        )

    def _trigger(self, player: PlayerOnScreen, npc: NpcOnScreen) -> Self:
        return replace(
            self,
            list=[
                n._trigger(player) if n.name == npc.name else n
                for n in self.list
            ],
        )


@dataclass(frozen=True)
class EventfulScene[T](Scene):
    """
    EventfulScene allows scenes to continue event execution via coroutine/
        generator.
    """

    _npcs: Npcs
    _npc: NpcOnScreen | None = None
    _event: RpgEventGenerator[T] | None = None
    _event_result: T | None = None

    def tick(self, time_delta: Millisecond) -> Self:
        return (
            self._next_event
            if self._next_event
            else self.tick_without_event(time_delta)
        )

    def tick_without_event(self, time_delta: Millisecond) -> Self:
        """
        Tick the scene without event execution.

        Arguments:
            `time_delta`: Time since last game loop.

        Returns:
            `Scene`: The scene without the next event.
        """
        return self

    def send(self, event: RpgEventGenerator, result: T | None = None) -> Self:
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

    def _trigger(self, player: PlayerOnScreen, npc: NpcOnScreen) -> Self:
        return replace(self, _npc=npc, _npcs=self._npcs._trigger(player, npc))

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
                _npcs=self._npcs._complete(self._npc),
                _npc=None,
                _event=None,
                _event_result=None,
            )


type RpgEventSpec = Callable[[PlayerOnScreen, NpcOnScreen, Npcs], None]
"""
Abstract protocol to define Rpg Event for player/NPC interactions.
"""

type RpgEventGenerator[T] = Generator[RpgEventCallable, T, None]
"""
The event generator type that can be used to yield an event.
"""

type RpgEventCallable[T] = Callable[
    [RpgEventGenerator[T], EventfulScene], RpgEventScene
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
    def _generator(
        self,
    ) -> Callable[[PlayerOnScreen, NpcOnScreen, Npcs], RpgEventGenerator[T]]:
        @wraps(self.event)
        def wraped(
            player: PlayerOnScreen, npc: NpcOnScreen, npcs: Npcs
        ) -> RpgEventGenerator:
            src = dedent(getsource(self.event))
            tree = fix_missing_locations(_yield.visit(parse(src)))
            code = compile(tree, "<npcs>", "exec")
            ctx = self.event.__globals__
            exec(code, ctx)
            return ctx[self.event.__name__](player, npc, npcs)

        return wraped


def _collide(player: PlayerOnScreen, npc: NpcOnScreen) -> bool:
    return npc.draw_on_screen.rectangle.collide(player.draw_on_screen.rectangle)
