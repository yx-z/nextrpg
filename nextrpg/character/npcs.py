from abc import ABC, abstractmethod
from collections.abc import Callable, Generator
from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import Self, override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_on_screen import (
    CharacterOnScreen,
    MovingCharacterOnScreen,
)
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.config import config
from nextrpg.core import Millisecond, PixelPerMillisecond, Timer
from nextrpg.draw_on_screen import Coordinate, Polygon
from nextrpg.event.pygame_event import KeyPressDown, KeyboardKey, PygameEvent
from nextrpg.event.rpg_event import RpgEventGenerator, wrap_spec, RpgEventSpec
from nextrpg.logger import Logger
from nextrpg.model import instance_init, register_instance_init
from nextrpg.scene.scene import Scene

logger = Logger("Npcs")


@dataclass(kw_only=True)
class NpcOnScreen(CharacterOnScreen):
    """
    In-game NPC interface, where NPC doesn't move.

    Arguments:
        `name`: Name of the NPC.

        `event_spec`: Event specification for player/NPC interactions.
    """

    name: str
    event_spec: RpgEventSpec
    _is_triggered: bool = False

    def tick(self, time_delta: Millisecond) -> Self:
        return replace(self, character=self.character.idle(time_delta))

    @cached_property
    def toggled(self) -> Self:
        return replace(self, _is_triggered=not self._is_triggered)


@register_instance_init
class MovingNpcOnScreen(MovingCharacterOnScreen, NpcOnScreen):
    """
    Moving NPC interface.

    Arguments:
        `path`: Polygon representing the path of the NPC.

        `idle_duration`: Duration of the idle state.

        `move_duration`: Duration of the moving state.
    """

    path: Polygon
    idle_duration: Millisecond
    move_duration: Millisecond
    _idle_timer: Timer = instance_init(lambda self: Timer(self.idle_duration))
    _move_timer: Timer = instance_init(lambda self: Timer(self.move_duration))
    _is_moving: bool = False

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        if self._is_moving:
            move_timer = self._move_timer.tick(time_delta)
            idle_timer = self._idle_timer
        else:
            move_timer = self._move_timer
            idle_timer = self._idle_timer.tick(time_delta)

        if self._is_moving and move_timer.expired:
            is_moving = False
        elif not self._is_moving and idle_timer.expired:
            is_moving = True
        else:
            is_moving = self._is_moving

        return replace(
            super().tick(time_delta),
            _idle_timer=idle_timer.reset() if is_moving else idle_timer,
            _move_timer=move_timer.reset() if not is_moving else move_timer,
            _is_moving=is_moving,
        )

    @cached_property
    @override
    def is_moving(self) -> bool:
        return self._is_moving and not self._is_triggered

    @override
    def move(self, time_delta: Millisecond) -> Coordinate:
        return self.coordinate


@register_instance_init
class Npcs[T]:
    """
    A collection of NPCs.

    Arguments:
        `list`: List of NPCs.
    """

    list: list[NpcOnScreen]

    @cached_property
    def dict(self) -> dict[str, NpcOnScreen]:
        return {n.name: n for n in self.list}

    def toggle(self, npc: NpcOnScreen) -> Self:
        return replace(
            self,
            list=[n.toggled if n.name == npc.name else n for n in self.list],
        )

    def event(
        self, event: PygameEvent, player: PlayerOnScreen, scene: EventfulScene
    ) -> Scene | None:
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
            logger.debug(t"Collied with {npc.name}")
            toggled_npcs = self.toggle(npc)
            toggled_scene = scene.toggle_npc(npc)
            generator = wrap_spec(npc.event_spec)(
                player, toggled_scene, toggled_npcs
            )
            return next(generator)(generator, toggled_scene)
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
        collide = (n for n in self.list if _collide_with_player(n, player))
        return next(collide, None)


@dataclass
class NpcSpec:
    """
    Base class to define NPC specifications.

    Arguments:
        `name`: Name of the NPC.

        `drawing`: Character drawing for the NPC.

        `event_spec`: Event specification for player/NPC interactions.
    """

    name: str
    character: CharacterDrawing
    event_spec: RpgEventSpec

    def draw_on_screen(self, coord: Coordinate) -> NpcOnScreen:
        """
        Draw the NPC on screen.

        Arguments:
            `coord`: The coordinate of the NPC on screen.

        Returns:
            `NpcOnScreen`: The NPC on screen.
        """
        return NpcOnScreen(
            coordinate=coord,
            character=self.character,
            event_spec=self.event_spec,
            name=self.name,
        )


@dataclass
class MovingNpcSpec(NpcSpec):
    """
    Moving NPC specification.

    Arguments:
        `move_speed`: Movement speed of the NPC in pixels per millisecond.

        `idle_duration`: Duration of the idle state.

        `move_duration`: Duration of the moving state.

        `observe_collisions`: Whether to observe collisions with the map.
    """

    move_speed: PixelPerMillisecond = field(
        default_factory=lambda: config().character.move_speed
    )
    idle_duration: Millisecond = field(
        default_factory=lambda: config().character.idle_duration
    )
    move_duration: Millisecond = field(
        default_factory=lambda: config().character.move_duration
    )
    observe_collisions: bool = True

    def draw_moving_on_screen(
        self, coord: Coordinate, path: Polygon, collisions: list[Polygon]
    ) -> MovingNpcOnScreen:
        return MovingNpcOnScreen(
            character=self.character,
            coordinate=coord,
            collisions=collisions,
            move_speed=self.move_speed,
            name=self.name,
            event_spec=self.event_spec,
            path=path,
            idle_duration=self.idle_duration,
            move_duration=self.move_duration,
        )


@dataclass
class EventfulScene[T](Scene, ABC):
    """
    EventfulScene allows scenes to continue event execution via coroutine/
        generator.
    """

    npcs: Npcs
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

    def toggle_npc(self, npc: NpcOnScreen) -> Self:
        return replace(self, _npc=npc, npcs=self.npcs.toggle(npc))

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
                npcs=self.npcs.toggle(self._npc),
                _npc=None,
                _event=None,
                _event_result=None,
            )


def _collide_with_player(npc: NpcOnScreen, player: PlayerOnScreen) -> bool:
    return npc.draw_on_screen.rectangle.collide(player.draw_on_screen.rectangle)
