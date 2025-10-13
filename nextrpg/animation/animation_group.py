from dataclasses import dataclass, replace
from typing import Self

from nextrpg.animation.abstract_animation import AbstractAnimation
from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.drawing.drawing_group import DrawingGroup


@dataclass(frozen=True)
class AnimationGroup(AbstractAnimation):
    resource: tuple[AnimationLike, ...]

    @property
    def is_complete(self) -> bool:
        return all(animation.is_complete for animation in self.resource)

    @property
    def drawing(self) -> DrawingGroup:
        relative_drawings = tuple(
            animation.no_shift for animation in self.resource
        )
        return DrawingGroup(relative_drawings)

    def _tick_before_complete(self, time_delta: Millisecond) -> Self:
        resource = tuple(
            animation.tick(time_delta) for animation in self.resource
        )
        return replace(self, resource=resource)
