from dataclasses import dataclass, replace
from functools import cached_property
from typing import TYPE_CHECKING, Self

from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.drawing.color import Alpha
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import (
    ZERO_SIZE,
    HeightScaling,
    Size,
    WidthAndHeightScaling,
    WidthScaling,
)

if TYPE_CHECKING:
    from nextrpg.drawing.drawing import Drawing
    from nextrpg.drawing.drawing_on_screen import DrawingOnScreen


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

    def __mul__(
        self, scaling: WidthScaling | HeightScaling | WidthAndHeightScaling
    ) -> Self:
        shift = self.shift * scaling
        resource = self.resource * scaling
        return replace(self, resource=resource, shift=shift)

    def tick(self, time_delta: Millisecond) -> Self:
        resource = self.resource.tick(time_delta)
        return replace(self, resource=resource)

    @cached_property
    def is_complete(self) -> bool:
        return self.resource.is_complete

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

    @cached_property
    def drawings(self) -> tuple[Drawing, ...]:
        return self.resource.drawings

    def drawing_on_screens(
        self, origin: Coordinate
    ) -> tuple[DrawingOnScreen, ...]:
        return self.resource.drawing_on_screens(
            origin + self.shift, self.anchor
        )


def relative_animation_likes(
    resource: (
        AnimationLike
        | RelativeAnimationLike
        | tuple[AnimationLike | RelativeAnimationLike, ...]
    ),
) -> tuple[RelativeAnimationLike, ...]:
    if isinstance(resource, tuple):
        return tuple(relative_animation_like(res) for res in resource)
    animation_like = relative_animation_like(resource)
    return (animation_like,)


def relative_animation_like(
    resource: AnimationLike | RelativeAnimationLike,
) -> RelativeAnimationLike:
    if isinstance(resource, AnimationLike):
        return resource.shift(ZERO_SIZE)
    return resource
