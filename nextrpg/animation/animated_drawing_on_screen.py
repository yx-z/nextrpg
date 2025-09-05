from dataclasses import dataclass, replace
from typing import Self, override

from nextrpg.animation.animation_on_screen import AnimationOnScreen
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing_on_screen import DrawingOnScreen


@dataclass(frozen=True)
class AnimatedDrawingOnScreen(AnimationOnScreen):
    resource: (
        AnimationOnScreen
        | DrawingOnScreen
        | tuple[AnimationOnScreen | DrawingOnScreen, ...]
    )

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        if isinstance(self.resource, DrawingOnScreen):
            return self
        if isinstance(self.resource, AnimationOnScreen):
            resource = self.resource.tick(time_delta)
            return replace(self, resource=resource)

        resources: list[AnimationOnScreen | DrawingOnScreen] = []
        for resource in self.resource:
            if isinstance(resource, AnimationOnScreen):
                res = resource.tick(time_delta)
            else:
                res = resource
            resources.append(res)
        return replace(self, resource=tuple(resources))

    @override
    @property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if isinstance(self.resource, AnimationOnScreen):
            return self.resource.drawing_on_screens
        if isinstance(self.resource, DrawingOnScreen):
            return (self.resource,)

        res: list[DrawingOnScreen] = []
        for resource in self.resource:
            if isinstance(resource, AnimationOnScreen):
                res += resource.drawing_on_screens
            else:
                res.append(resource)
        return tuple(res)

    @override
    @property
    def complete(self) -> bool:
        if isinstance(self.resource, AnimationOnScreen):
            return self.resource.complete
        if isinstance(self.resource, DrawingOnScreen):
            return True
        return all(
            (
                resource.complete
                if isinstance(resource, AnimationOnScreen)
                else True
            )
            for resource in self.resource
        )
