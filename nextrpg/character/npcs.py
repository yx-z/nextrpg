from ast import fix_missing_locations, parse
from collections.abc import Callable, Generator
from dataclasses import dataclass, field, replace
from functools import cached_property, wraps
from inspect import getsource
from textwrap import dedent
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
from nextrpg.event.rpg_event import _yield
from nextrpg.logger import Logger
from nextrpg.model import instance_init, register_instance_init
from nextrpg.scene.map_helper import MapHelper, get_polygon
from nextrpg.scene.scene import Scene

logger = Logger("Npcs")


type RpgEventSpec = Callable[[PlayerOnScreen, NpcOnScreen, Npcs], None]
"""
Abstract protocol to define Rpg Event for player/NPC interactions.
"""


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

    def tick(self, time_delta: Millisecond) -> Self:
        return replace(self, character=self.character.idle(time_delta))


@register_instance_init
class MovingNpcOnScreen(NpcOnScreen, MovingCharacterOnScreen):
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
        return self._is_moving

    @override
    def move(self, time_delta: Millisecond) -> Coordinate:
        return self.coordinate


def _init_npcs(self: Npcs) -> list[NpcOnScreen]:
    return [
        (self._init_move(n) if isinstance(n, MovingNpcSpec) else self._init(n))
        for n in self.specs
    ]


@register_instance_init
class Npcs:
    """
    A collection of NPCs.

    Arguments:
        `map_helper`: The map helper to retrieve NPCs from the map.

        `specs`: List of NPC specifications.
    """

    map_helper: MapHelper
    specs: list[NpcSpec] = field(default_factory=list)
    list: list[NpcOnScreen] = instance_init(_init_npcs)

    def trigger(self, player: PlayerOnScreen, scene: Scene) -> Scene | None:
        """
        Trigger the NPC event.

        `Arguments`:
            `player`: The current player.

            `scene`: The current scene.

        Returns:
            `Scene`: The scene after the event is triggered, if any.
        """
        if npc := self._collided_npc(player):
            logger.debug(t"Collied with {npc.name}")
            generator = _wrap_spec(npc.event_spec)(player, npc, self)
            return next(generator)(generator, scene)
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

    def _init(self, spec: NpcSpec) -> NpcOnScreen:
        obj = self.map_helper.get_object(spec.name)
        return NpcOnScreen(
            character=spec.drawing,
            coordinate=Coordinate(obj.x, obj.y),
            event_spec=spec.event_spec,
            name=spec.name,
        )

    def _init_move(self, spec: MovingNpcSpec) -> MovingNpcOnScreen:
        obj = self.map_helper.get_object(spec.name)
        collisions = (
            self.map_helper.collisions if spec.observe_collisions else []
        )
        return MovingNpcOnScreen(
            character=spec.drawing,
            coordinate=Coordinate(obj.x, obj.y),
            collisions=collisions,
            move_speed=spec.move_speed,
            name=spec.name,
            event_spec=spec.event_spec,
            path=get_polygon(obj),
            idle_duration=spec.idle_duration,
            move_duration=spec.move_duration,
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
    drawing: CharacterDrawing
    event_spec: RpgEventSpec


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


def _collide_with_player(npc: NpcOnScreen, player: PlayerOnScreen) -> bool:
    return npc.draw_on_screen.rectangle.collide(player.draw_on_screen.rectangle)


type RpgEventGenerator[T] = Generator[RpgEventCallable, T, None]
type RpgEventCallable[T] = Callable[[RpgEventGenerator[T], Scene], Scene]


def _wrap_spec(
    fun: RpgEventSpec,
) -> Callable[[PlayerOnScreen, NpcOnScreen, Npcs], RpgEventGenerator]:
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
