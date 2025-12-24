from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.base_animation_on_screen import (
    BaseAnimationOnScreen,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screens import (
    DrawingOnScreens,
    drawing_on_screens,
)
from nextrpg.drawing.sprite import tick_all
from nextrpg.drawing.sprite_on_screen import (
    SpriteOnScreen,
)


@dataclass(frozen=True)
class AnimationOnScreens(BaseAnimationOnScreen):
    resource: SpriteOnScreen | tuple[SpriteOnScreen, ...]

    @cached_property
    def resources(self) -> tuple[SpriteOnScreen, ...]:
        if isinstance(self.resource, SpriteOnScreen):
            return (self.resource,)
        return self.resource

    def concur(self, another: SpriteOnScreen) -> AnimationOnScreens:
        return AnimationOnScreens((self, another))

    @override
    @cached_property
    def drawing_on_screens(self) -> DrawingOnScreens:
        return drawing_on_screens(self.resources)

    @override
    @cached_property
    def is_complete(self) -> bool:
        return all(resource.is_complete for resource in self.resources)

    @override
    def _tick_before_complete(self, time_delta: Millisecond) -> Self:
        resource = tick_all(self.resources, time_delta)
        return replace(self, resource=resource)
