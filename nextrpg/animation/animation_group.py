from dataclasses import dataclass, replace
from typing import Self

from nextrpg.animation.abstract_animation import AbstractAnimation
from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.drawing.drawing_group import DrawingGroup


@dataclass(frozen=True)
class AnimationGroup(AbstractAnimation):
    resource: AnimationLike | tuple[AnimationLike, ...]

    @property
    def is_complete(self) -> bool:
        if isinstance(self.resource, tuple):
            return all(animation.is_complete for animation in self.resource)
        return self.resource.is_complete

    @property
    def drawing(self) -> DrawingGroup:
        if isinstance(self.resource, tuple):
            relative_drawings = tuple(
                animation.no_shift for animation in self.resource
            )
        else:
            relative_drawings = self.resource.no_shift
        return DrawingGroup(relative_drawings)

    def _tick_before_complete(self, time_delta: Millisecond) -> Self:
        if isinstance(self.resource, tuple):
            resource = tuple(
                animation.tick(time_delta) for animation in self.resource
            )
        else:
            resource = self.resource.tick(time_delta)
        return replace(self, resource=resource)
