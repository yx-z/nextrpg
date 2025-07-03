from dataclasses import KW_ONLY, dataclass, field, replace
from functools import cached_property
from typing import override

from nextrpg.character.character_on_screen import (
    CharacterOnScreen,
    MovingCharacterOnScreen,
)
from nextrpg.core import Millisecond, Timer
from nextrpg.draw_on_screen import Polygon
from nextrpg.event.pygame_event import PygameEvent
from nextrpg.model import instance_init, register_instance_init


class Npc(CharacterOnScreen):
    def event(self, e: PygameEvent) -> CharacterOnScreen:
        pass


@dataclass
class StaticNpcOnScreen(Npc):
    def tick(self, time_delta: Millisecond) -> CharacterOnScreen:
        return replace(self, character=self.character.idle(time_delta))


@register_instance_init
class MovingNpcOnScreen(Npc, MovingCharacterOnScreen):
    _: KW_ONLY = field()
    path: Polygon = field()
    idle_duration: Millisecond
    move_duration: Millisecond
    _idle_timer: Timer = instance_init(lambda self: Timer(self.idle_duration))
    _move_timer: Timer = instance_init(lambda self: Timer(self.move_duration))
    _is_moving: bool = False

    @override
    def tick(self, time_delta: Millisecond) -> CharacterOnScreen:
        if self._is_moving:
            move_timer = self._move_timer.tick(time_delta)
            idle_timer = self._idle_timer
        else:
            move_timer = self._move_timer
            idle_timer = self._idle_timer.tick(time_delta)

        is_moving = self._is_moving
        if self._is_moving and move_timer.expired:
            is_moving = False
        if not self._is_moving and idle_timer.expired:
            is_moving = True

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
