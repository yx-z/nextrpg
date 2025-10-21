from abc import ABC, abstractmethod
from functools import cached_property
from typing import override

from nextrpg.animation.timed_animation_group import TimedAnimationGroup
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
)
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.geometry.direction import DirectionalOffset


@dataclass_with_default(frozen=True, kw_only=True)
class Move(TimedAnimationGroup, ABC):
    offset: DirectionalOffset

    @override
    @cached_property
    def drawing(self) -> DrawingGroup:
        drawing = super().drawing
        resource = tuple(
            relative_drawing + (self.move_percentage * self.offset).shift
            for relative_drawing in drawing.resources
        )
        return DrawingGroup(resource)

    @property
    @abstractmethod
    def move_percentage(self) -> float: ...


class MoveFrom(Move):
    @override
    @cached_property
    def move_percentage(self) -> float:
        return min(self._timer.completed_percentage, 1)


class MoveTo(Move):
    @override
    @cached_property
    def move_percentage(self) -> float:
        return min(-self._timer.remaining_percentage, 0)
