from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import NamedTuple, Self, override

from nextrpg.character.character_on_screen import MovingCharacterOnScreen
from nextrpg.character.npcs import NpcOnScreen, NpcSpec
from nextrpg.config import config
from nextrpg.core import Millisecond, PixelPerMillisecond, Timer
from nextrpg.draw_on_screen import Polygon
from nextrpg.coordinate import Coordinate
from nextrpg.model import instance_init, dataclass_with_instance_init
from nextrpg.walk import Walk


@dataclass(frozen=True)
class MovingNpcSpec(NpcSpec):
    """
    Moving NPC specification.

    Arguments:
        `move_speed`: Movement speed of the NPC in pixels per millisecond.

        `idle_duration`: Duration of the idle state.

        `move_duration`: Duration of the moving state.
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
    cyclic_walk: bool = True


@dataclass_with_instance_init
class MovingNpcOnScreen(NpcOnScreen, MovingCharacterOnScreen):
    """
    Moving NPC interface.

    Arguments:
        `path`: Polygon representing the path of the NPC.

        `idle_duration`: Duration of the idle state.

        `move_duration`: Duration of the moving state.
    """

    path: Polygon
    spec: MovingNpcSpec
    collisions: tuple[Polygon, ...] = field(default_factory=tuple)
    move_speed: PixelPerMillisecond = instance_init(
        lambda self: self.spec.move_speed
    )
    _walk: Walk = instance_init(
        lambda self: Walk(
            path=self.path,
            move_speed=self.move_speed,
            cyclic=self.spec.cyclic_walk,
        )
    )
    _idle_timer: Timer = instance_init(
        lambda self: Timer(self.spec.idle_duration)
    )
    _move_timer: Timer = instance_init(
        lambda self: Timer(self.spec.move_duration)
    )
    _moving: bool = True

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        if self._triggered:
            return self

        move_timer, idle_timer, moving = self._timers_and_moving(time_delta)
        if moving:
            moved = MovingCharacterOnScreen.tick(self, time_delta)
            walked = self._walk.tick(time_delta)
            return replace(
                moved,
                character=moved.character.turn(walked.direction),
                _walk=walked,
                _idle_timer=idle_timer.reset,
                _move_timer=move_timer,
                _moving=moving,
            )
        return replace(
            NpcOnScreen.tick(self, time_delta),
            _idle_timer=idle_timer,
            _move_timer=move_timer.reset,
            _moving=moving,
        )

    @cached_property
    @override
    def moving(self) -> bool:
        return self._moving and not self._triggered

    @override
    def move(self, time_delta: Millisecond) -> Coordinate:
        return self._walk.tick(time_delta).coordinate

    def _timers_and_moving(self, time_delta: Millisecond) -> _TimerAndMoving:
        if self._moving:
            move_timer = self._move_timer.tick(time_delta)
            idle_timer = self._idle_timer
        else:
            move_timer = self._move_timer
            idle_timer = self._idle_timer.tick(time_delta)

        if self._moving and move_timer.complete:
            moving = False
        elif not self._moving and idle_timer.complete:
            moving = True
        else:
            moving = self._moving

        return _TimerAndMoving(move_timer, idle_timer, moving)


class _TimerAndMoving(NamedTuple):
    move_timer: Timer
    idle_timer: Timer
    moving: bool
