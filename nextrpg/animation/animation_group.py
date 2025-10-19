from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.abstract_animation import (
    AbstractAnimation,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.drawing.relative_animation_like import (
    RelativeAnimationLike,
    relative_animation_likes,
)


@dataclass(frozen=True)
class AnimationGroup(AbstractAnimation):
    resource: (
        AnimationLike
        | RelativeAnimationLike
        | tuple[AnimationLike | RelativeAnimationLike, ...]
    )

    def concur(self, another: RelativeAnimationLike) -> Self:
        resource = (*self.resources, another)
        return replace(self, resource=resource)

    @cached_property
    def resources(self) -> tuple[RelativeAnimationLike, ...]:
        return relative_animation_likes(self.resource)

    @override
    @cached_property
    def is_complete(self) -> bool:
        return all(
            relative_drawing.is_complete for relative_drawing in self.resources
        )

    @override
    @cached_property
    def drawing(self) -> DrawingGroup:
        return DrawingGroup(self.resources)

    @override
    def _tick_before_complete(self, time_delta: Millisecond) -> Self:
        resource = tuple(
            relative_drawing.tick(time_delta)
            for relative_drawing in self.resources
        )
        return replace(self, resource=resource)
