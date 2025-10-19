from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self

from nextrpg.core.time import Millisecond
from nextrpg.drawing.anchor import Anchor
from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.drawing.color import Alpha
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import (
    ZERO_SIZE,
    HeightScaling,
    Size,
    WidthAndHeightScaling,
    WidthScaling,
)


@dataclass(frozen=True)
class RelativeAnimationLike:
    resource: AnimationLike
    shift: Size
    anchor: Anchor = Anchor.TOP_LEFT

    def __add__(self, other: Size) -> Self:
        shift = self.shift + other
        return replace(self, shift=shift)

    def __sub__(self, other: Size) -> Self:
        return self + -other

    def tick(self, time_delta: Millisecond) -> Self:
        resource = self.resource.tick(time_delta)
        return replace(self, resource=resource)

    @cached_property
    def is_complete(self) -> bool:
        return self.resource.is_complete

    def top_left(self, origin: Coordinate) -> Coordinate:
        match self.anchor:
            case Anchor.TOP_LEFT:
                extra = ZERO_SIZE
            case Anchor.TOP_CENTER:
                extra = self.resource.width / 2
            case Anchor.TOP_RIGHT:
                extra = self.resource.width
            case Anchor.CENTER_LEFT:
                extra = self.resource.height / 2
            case Anchor.CENTER:
                extra = self.resource.size / WidthAndHeightScaling(2)
            case Anchor.CENTER_RIGHT:
                extra = self.resource.size / HeightScaling(2)
            case Anchor.BOTTOM_LEFT:
                extra = self.resource.height
            case Anchor.BOTTOM_CENTER:
                extra = self.resource.size / WidthScaling(2)
            case Anchor.BOTTOM_RIGHT:
                extra = self.resource.size
        return origin + self.shift - extra

    def flip(self, horizontal: bool = False, vertical: bool = False) -> Self:
        resource = self.resource.flip(horizontal, vertical)
        shift = self.shift
        if horizontal:
            shift = shift.negate_width
        if vertical:
            shift = shift.negate_height
        anchor = -self.anchor
        return replace(self, resource=resource, shift=shift, anchor=anchor)

    def alpha(self, alpha: Alpha) -> Self:
        resource = self.resource.alpha(alpha)
        return replace(self, resource=resource)


def relative_animation_likes(
    resource: (
        AnimationLike
        | RelativeAnimationLike
        | tuple[AnimationLike | RelativeAnimationLike, ...]
    ),
) -> tuple[RelativeAnimationLike, ...]:
    if isinstance(resource, tuple):
        return tuple(relative_animation_like(res) for res in resource)
    return (relative_animation_like(resource),)


def relative_animation_like(
    resource: AnimationLike | RelativeAnimationLike,
) -> RelativeAnimationLike:
    if isinstance(resource, AnimationLike):
        return RelativeAnimationLike(resource, ZERO_SIZE)
    return resource
