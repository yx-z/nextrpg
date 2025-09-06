from abc import abstractmethod
from dataclasses import KW_ONLY, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.animation_on_screens import AnimationOnScreens
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond, Timer
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.geometry.direction import DirectionalOffset


@dataclass_with_default(frozen=True)
class Move(AnimationOnScreens):
    offset: DirectionalOffset
    duration: Millisecond
    _: KW_ONLY = private_init_below()
    _timer: Timer = default(lambda self: Timer(self.duration))

    @override
    @property
    def is_complete(self) -> bool:
        return self._timer.overdue

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        ticked = super().tick(time_delta)
        timer = self._timer.tick(time_delta)
        return replace(ticked, _timer=timer)

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return tuple(
            drawing_on_screen + self.offset * self._percentage
            for drawing_on_screen in super().drawing_on_screens
        )

    @property
    @abstractmethod
    def _percentage(self) -> float: ...


class MoveFrom(Move):
    @override
    @property
    def _percentage(self) -> float:
        return self._timer.completed_percentage


class MoveTo(Move):
    @override
    @property
    def _percentage(self) -> float:
        return -self._timer.remaining_percentage
