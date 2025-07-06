from dataclasses import replace
from functools import cached_property
from typing import Self, override

from nextrpg.character.character_on_screen import MovingCharacterOnScreen
from nextrpg.character.npcs import NpcOnScreen
from nextrpg.core import Millisecond, Timer
from nextrpg.draw_on_screen import Coordinate, Polygon
from nextrpg.model import instance_init, register_instance_init


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
