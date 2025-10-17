from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.abstract_animation import AbstractAnimation
from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.drawing.relative_drawing import RelativeDrawing


@dataclass(frozen=True)
class AnimationGroup(AbstractAnimation):
    resource: RelativeDrawing | tuple[RelativeDrawing, ...]

    def concur(self, another: RelativeDrawing) -> AnimationGroup:
        resource = (self.no_shift, another)
        return AnimationGroup(resource)

    @override
    @cached_property
    def is_complete(self) -> bool:
        if isinstance(self.resource, tuple):
            return all(
                relative_drawing.drawing.is_complete
                for relative_drawing in self.resource
            )
        return self.resource.drawing.is_complete

    @override
    @cached_property
    def drawing(self) -> Drawing | DrawingGroup:
        return DrawingGroup(self.resource)

    @override
    def _tick_before_complete(self, time_delta: Millisecond) -> Self:
        if isinstance(self.resource, tuple):
            resource = tuple(
                relative_drawing.tick(time_delta)
                for relative_drawing in self.resource
            )
        else:
            resource = self.resource.tick(time_delta)
        return replace(self, resource=resource)
