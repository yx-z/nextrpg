from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.animation_on_screen import AnimationOnScreen
from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen


@dataclass(frozen=True)
class AnimationOnScreens(AnimationOnScreen):
    resource: (
        AnimationOnScreen
        | DrawingOnScreen
        | tuple[AnimationOnScreen | DrawingOnScreen, ...]
    )

    @override
    def tick_before_complete(self, time_delta: Millisecond) -> Self:
        if isinstance(self.resource, DrawingOnScreen | AnimationOnScreen):
            resource = self.resource.tick_before_complete(time_delta)
            return replace(self, resource=resource)
        resources = tuple(
            resource.tick_before_complete(time_delta)
            for resource in self.resource
        )
        return replace(self, resource=tuple(resources))

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if isinstance(self.resource, AnimationOnScreen | DrawingOnScreen):
            return self.resource.drawing_on_screens
        return tuple(
            drawing_on_screen
            for resource in self.resource
            for drawing_on_screen in resource.drawing_on_screens
        )

    @override
    @cached_property
    def is_complete(self) -> bool:
        if isinstance(self.resource, AnimationOnScreen | DrawingOnScreen):
            return self.resource.is_complete
        return all(resource.is_complete for resource in self.resource)
