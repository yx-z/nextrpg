from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.abstract_animation_on_screen import (
    AbstractAnimationOnScreen,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.sprite_on_screen import (
    SpriteOnScreen,
    tick_all,
)


@dataclass(frozen=True)
class AnimationOnScreens(AbstractAnimationOnScreen):
    resource: SpriteOnScreen | tuple[SpriteOnScreen, ...]

    @cached_property
    def resources(self) -> tuple[SpriteOnScreen, ...]:
        if isinstance(self.resource, SpriteOnScreen):
            return (self.resource,)
        return self.resource

    def concur(self, another: SpriteOnScreen) -> AnimationOnScreens:
        resources = (self, another)
        return AnimationOnScreens(resources)

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return tuple(
            drawing_on_screen
            for resource in self.resources
            for drawing_on_screen in resource.drawing_on_screens
        )

    @override
    @cached_property
    def is_complete(self) -> bool:
        return all(resource.is_complete for resource in self.resources)

    @override
    def _tick_before_complete(self, time_delta: Millisecond) -> Self:
        resource = tick_all(self.resources, time_delta)
        return replace(self, resource=resource)
