from dataclasses import dataclass, replace
from functools import cached_property
from typing import Any, Self

from nextrpg.animation.animation_on_screens import AnimationOnScreens
from nextrpg.animation.timed_animation_group import TimedAnimationGroup
from nextrpg.animation.timed_animation_on_screen import TimedAnimationOnScreen


@dataclass(frozen=True)
class TimedAnimationOnScreens(AnimationOnScreens):
    resource: TimedAnimationOnScreen | tuple[TimedAnimationOnScreen, ...]

    @cached_property
    def resources(self) -> tuple[TimedAnimationOnScreen, ...]:
        if isinstance(self.resource, TimedAnimationOnScreen):
            return (self.resource,)
        return self.resource

    def compose(self, other: type[TimedAnimationGroup], **kwargs: Any) -> Self:
        resources = tuple(
            res.compose(other, **kwargs) for res in self.resources
        )
        return replace(self, resource=resources)

    @cached_property
    def reversed(self) -> Self:
        resources = tuple(res.reversed for res in self.resources)
        return replace(self, resource=resources)
