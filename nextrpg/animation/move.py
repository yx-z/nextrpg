from abc import ABC, abstractmethod
from functools import cached_property
from typing import override

from nextrpg.animation.timed_animation_group import TimedAnimationGroup
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
)
from nextrpg.core.util import Percentage
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.directional_offset import DirectionalOffset
from nextrpg.geometry.size import Size


@dataclass_with_default(frozen=True, kw_only=True)
class Move(TimedAnimationGroup, ABC):
    offset: Coordinate | Size | DirectionalOffset

    @override
    @cached_property
    def drawing(self) -> DrawingGroup:
        drawing = super().drawing
        resource = tuple(
            relative_drawing
            + self.offset.directional_offset * self.move_percentage
            for relative_drawing in drawing.resources
        )
        return DrawingGroup(resource)

    @property
    @abstractmethod
    def move_percentage(self) -> Percentage: ...


class MoveFrom(Move):
    @override
    @cached_property
    def move_percentage(self) -> Percentage:
        return min(self._timer.completed_percentage, 1)


class MoveTo(Move):
    @override
    @cached_property
    def move_percentage(self) -> Percentage:
        return min(-self._timer.remaining_percentage, 0)
