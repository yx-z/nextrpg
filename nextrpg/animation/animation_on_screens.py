from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.abstract_animation_on_screen import (
    AbstractAnimationOnScreen,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_on_screen_like import (
    AnimationOnScreenLike,
)
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen


@dataclass(frozen=True)
class AnimationOnScreens(AbstractAnimationOnScreen):
    resource: AnimationOnScreenLike | tuple[AnimationOnScreenLike, ...]

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if isinstance(self.resource, tuple):
            return tuple(
                drawing_on_screen
                for resource in self.resource
                for drawing_on_screen in resource.drawing_on_screens
            )
        return self.resource.drawing_on_screens

    @override
    @cached_property
    def is_complete(self) -> bool:
        if isinstance(self.resource, tuple):
            return all(resource.is_complete for resource in self.resource)
        return self.resource.is_complete

    @override
    def _tick_before_complete(self, time_delta: Millisecond) -> Self:
        if isinstance(self.resource, tuple):
            resources = tuple(
                resource.tick(time_delta) for resource in self.resource
            )
            return replace(self, resource=tuple(resources))
        resource = self.resource.tick(time_delta)
        return replace(self, resource=resource)
