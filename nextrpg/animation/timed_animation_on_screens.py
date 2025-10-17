from dataclasses import replace
from functools import cached_property
from typing import Self, TypeVar

from nextrpg.animation.animation_on_screens import AnimationOnScreens
from nextrpg.animation.timed_animation_group import TimedAnimationGroup
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
)

_T = TypeVar("_T", bound="TimedAnimationGroup")


@dataclass_with_default(frozen=True)
class TimedAnimationOnScreens(AnimationOnScreens):
    resource: TimedAnimationGroup | tuple[TimedAnimationGroup, ...]

    def compose(self, other: type[_T]) -> Self:
        if isinstance(self.resource, tuple):
            resource = tuple(
                resource.compose(other) for resource in self.resource
            )
        else:
            resource = self.resource.compose(other)
        return replace(self, resource=resource)

    @cached_property
    def reverse(self) -> Self:
        if isinstance(self.resource, tuple):
            resource = tuple(resource.reverse for resource in self.resource)
        else:
            resource = self.resource.reverse
        return replace(self, resource=resource)
