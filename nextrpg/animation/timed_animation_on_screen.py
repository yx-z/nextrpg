from dataclasses import dataclass, replace
from functools import cached_property
from typing import Any, Self

from nextrpg.animation.animation_on_screen import AnimationOnScreen
from nextrpg.animation.timed_animation_group import TimedAnimationGroup


@dataclass(frozen=True)
class TimedAnimationOnScreen(AnimationOnScreen):
    resource: TimedAnimationGroup

    def compose(self, other: type[TimedAnimationGroup], **kwargs: Any) -> Self:
        resource = self.resource.compose(other, **kwargs)
        return replace(self, resource=resource)

    @cached_property
    def reversed(self) -> Self:
        resource = self.resource.reversed
        return replace(self, resource=resource)
