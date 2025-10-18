from dataclasses import dataclass, replace
from functools import cached_property
from typing import Any, Self, TypeVar

from nextrpg.animation.animation_on_screens import AnimationOnScreens
from nextrpg.animation.timed_animation_group import TimedAnimationGroup
from nextrpg.animation.timed_animation_on_screen import TimedAnimationOnScreen

_T = TypeVar("_T", bound=TimedAnimationGroup)


@dataclass(frozen=True)
class TimedAnimationOnScreens(AnimationOnScreens):
    resource: TimedAnimationOnScreen | tuple[TimedAnimationOnScreen, ...]

    @cached_property
    def resources(self) -> tuple[TimedAnimationOnScreen, ...]:
        if isinstance(self.resource, tuple):
            return self.resource
        return (self.resource,)

    def compose(self, other: type[_T], **kwargs: Any) -> Self:
        resources = tuple(
            res.compose(other, **kwargs) for res in self.resources
        )
        return replace(self, resource=resources)

    @cached_property
    def reverse(self) -> Self:
        resources = tuple(res.reverse for res in self.resources)
        return replace(self, resource=resources)
