from abc import abstractmethod
from functools import cached_property
from typing import override

from nextrpg.animation.timed_animation_on_screens import TimedAnimationOnScreens
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
)
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.geometry.direction import DirectionalOffset


@dataclass_with_default(frozen=True, kw_only=True)
class Move(TimedAnimationOnScreens):
    offset: DirectionalOffset

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
