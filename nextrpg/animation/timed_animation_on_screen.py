from dataclasses import dataclass, replace
from functools import cached_property
from typing import Any, Self, TypeVar

from nextrpg.animation.animation_on_screen import AnimationOnScreen
from nextrpg.animation.timed_animation_group import TimedAnimationGroup

_T = TypeVar("_T", bound=TimedAnimationGroup)


@dataclass(frozen=True)
class TimedAnimationOnScreen(AnimationOnScreen):
    resource: TimedAnimationGroup

    def compose(self, other: type[_T], **kwargs: Any) -> Self:
        resource = self.resource.compose(other, **kwargs)
        return replace(self, resource=resource)

    @cached_property
    def reverse(self) -> Self:
        resource = self.resource.reverse
        return replace(self, resource=resource)
