from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import Self, override

from nextrpg.character.character_on_screen import MovingCharacterOnScreen
from nextrpg.character.npcs import NpcOnScreen, NpcSpec
from nextrpg.config import config
from nextrpg.core import Millisecond, PixelPerMillisecond, Timer
from nextrpg.draw_on_screen import Coordinate, Polygon
from nextrpg.model import instance_init, register_instance_init


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
    _idle_timer: Timer = instance_init(
        lambda self: Timer(self.spec.idle_duration)
    )
    _move_timer: Timer = instance_init(
        lambda self: Timer(self.spec.move_duration)
    )
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
            MovingCharacterOnScreen.tick(self, time_delta),
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
        if not self.is_moving:
            return self.coordinate
        return self.coordinate
