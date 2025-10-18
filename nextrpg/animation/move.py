from abc import abstractmethod
from functools import cached_property
from typing import override

from nextrpg.animation.timed_animation_group import TimedAnimationGroup
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
)
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.geometry.direction import DirectionalOffset


@dataclass_with_default(frozen=True, kw_only=True)
class Move(TimedAnimationGroup):
    offset: DirectionalOffset

    @override
    @cached_property
    def drawing(self) -> DrawingGroup:
        drawing = super().drawing
        resource = tuple(
            relative_drawing + (self._percentage * self.offset).shift
            for relative_drawing in drawing.resources
        )
        return DrawingGroup(resource)

    @property
    @abstractmethod
    def _percentage(self) -> float: ...


class MoveFrom(Move):
    @override
    @cached_property
    def _percentage(self) -> float:
        return self._timer.completed_percentage


class MoveTo(Move):
    @override
    @cached_property
    def _percentage(self) -> float:
        return -self._timer.remaining_percentage
