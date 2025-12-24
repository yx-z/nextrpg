from collections.abc import Iterable
from dataclasses import dataclass, replace
from functools import cached_property
from typing import TYPE_CHECKING, Self

from nextrpg.core.time import Millisecond
from nextrpg.drawing.color import Alpha
from nextrpg.drawing.sprite import BlurRadius, Sprite
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.directional_offset import Degree, DirectionalOffset
from nextrpg.geometry.scaling import (
    HeightScaling,
    WidthAndHeightScaling,
    WidthScaling,
)
from nextrpg.geometry.size import ZERO_SIZE, Height, Size, Width

if TYPE_CHECKING:
    from nextrpg.drawing.drawing import Drawing
    from nextrpg.drawing.drawing_group import DrawingGroup
    from nextrpg.drawing.drawing_on_screens import DrawingOnScreens


@dataclass(frozen=True)
class ShiftedSprite:
    resource: Sprite
    offset: Coordinate | Width | Height | Size | DirectionalOffset
    anchor: Anchor = Anchor.TOP_LEFT

    @cached_property
    def offset_size(self) -> Size:
        return self.offset.size

    @cached_property
    def drawing_group(self) -> DrawingGroup:
        from nextrpg.drawing.drawing_group import DrawingGroup

        return DrawingGroup(self)

    def __add__(
        self, other: Coordinate | Width | Height | Size | DirectionalOffset
    ) -> Self:
        offset = self.offset_size + other.size
        return replace(self, offset=offset)

    def __sub__(
        self, other: Coordinate | Width | Height | Size | DirectionalOffset
    ) -> Self:
        return self + -other

    def __mul__(
        self, scaling: WidthScaling | HeightScaling | WidthAndHeightScaling
    ) -> Self:
        offset = self.offset_size * scaling
        resource = self.resource * scaling
        return replace(self, resource=resource, offset=offset)

    def tick(self, time_delta: Millisecond) -> Self:
        resource = self.resource.tick(time_delta)
        return replace(self, resource=resource)

    @cached_property
    def is_complete(self) -> bool:
        return self.resource.is_complete

    def flip(self, horizontal: bool = False, vertical: bool = False) -> Self:
        resource = self.resource.flip(horizontal, vertical)
        offset = self.offset_size
        if horizontal:
            offset = offset.negate_width
        if vertical:
            offset = offset.negate_height
        anchor = -self.anchor
        return replace(self, resource=resource, offset=offset, anchor=anchor)

    def alpha(self, alpha: Alpha) -> Self:
        resource = self.resource.alpha(alpha)
        return replace(self, resource=resource)

    @cached_property
    def drawings(self) -> tuple[Drawing, ...]:
        return self.resource.drawings

    def drawing_on_screens(self, origin: Coordinate) -> DrawingOnScreens:
        return self.resource.drawing_on_screens(
            origin + self.offset_size, self.anchor
        )

    def blur(self, radius: BlurRadius) -> Self:
        resource = self.resource.blur(radius)
        return replace(self, resource=resource)

    def rotate(self, degree: Degree) -> Self:
        offset = self.offset_size.directional_offset
        rotated = replace(offset, degree=offset.degree + degree)
        return replace(self, offset=rotated)


def shifted_sprites(
    resource: Sprite | ShiftedSprite | Iterable[Sprite | ShiftedSprite],
) -> tuple[ShiftedSprite, ...]:
    if isinstance(resource, Sprite | ShiftedSprite):
        sprite = shifted_sprite(resource)
        return (sprite,)
    return tuple(shifted_sprite(res) for res in resource)


def shifted_sprite(
    resource: Sprite | ShiftedSprite,
) -> ShiftedSprite:
    if isinstance(resource, Sprite):
        return resource + ZERO_SIZE
    return resource
