from dataclasses import dataclass, replace
from functools import cached_property
from typing import TYPE_CHECKING, Self, override

from pygame import Surface

from nextrpg.core.metadata import HasMetadata, Metadata
from nextrpg.core.time import Millisecond
from nextrpg.drawing.color import Alpha
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.drawing.shifted_sprite import (
    ShiftedSprite,
    shifted_sprites,
)
from nextrpg.drawing.sprite import BlurRadius, Sprite, tick_all
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.coordinate import ORIGIN, Coordinate
from nextrpg.geometry.directional_offset import Degree
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.geometry.scaling import HeightScaling, WidthScaling
from nextrpg.geometry.size import Size

if TYPE_CHECKING:
    from nextrpg.drawing.drawing_group_on_screen import DrawingGroupOnScreen


@dataclass(frozen=True)
class DrawingGroup(Sprite, HasMetadata):
    resource: Sprite | ShiftedSprite | tuple[Sprite | ShiftedSprite, ...]
    metadata: Metadata = ()

    @override
    @cached_property
    def is_complete(self) -> bool:
        return all(res.is_complete for res in self.resources)

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        resources = tick_all(self.resources, time_delta)
        return replace(self, resource=resources)

    @cached_property
    def resources(self) -> tuple[ShiftedSprite, ...]:
        return shifted_sprites(self.resource)

    @override
    def alpha(self, alpha: Alpha) -> Self:
        resources = tuple(res.alpha(alpha) for res in self.resources)
        return replace(self, resource=resources)

    def __mul__(
        self, scaling: WidthScaling | HeightScaling | WidthScaling
    ) -> Self:
        resource = tuple(res * scaling for res in self.resources)
        return replace(self, resource=resource)

    @override
    @cached_property
    def drawing(self) -> DrawingGroup:
        return self

    @override
    @cached_property
    def drawings(self) -> tuple[Drawing, ...]:
        return tuple(d for res in self.resources for d in res.drawings)

    @override
    def drawing_on_screens(
        self, coordinate: Coordinate, anchor: Anchor = Anchor.TOP_LEFT
    ) -> DrawingOnScreens:
        return self.drawing_group_on_screen(
            coordinate, anchor
        ).drawing_on_screens

    def drawing_group_on_screen(
        self, coordinate: Coordinate, anchor: Anchor = Anchor.TOP_LEFT
    ) -> DrawingGroupOnScreen:
        from nextrpg.drawing.drawing_group_on_screen import DrawingGroupOnScreen

        origin = coordinate.as_anchor_of(self, anchor).top_left
        return DrawingGroupOnScreen(origin, self)

    @override
    @cached_property
    def size(self) -> Size:
        return self._drawing_group_on_screen.size

    @override
    @cached_property
    def top_left(self) -> Coordinate:
        return self._drawing_group_on_screen.top_left

    def flip(self, horizontal: bool = False, vertical: bool = False) -> Self:
        resource = tuple(
            relative_drawing.flip(horizontal, vertical)
            for relative_drawing in self.resources
        )
        return replace(self, resource=resource)

    @override
    def cut(self, area: RectangleAreaOnScreen) -> Self:
        res: list[ShiftedSprite] = []
        for relative in self.resources:
            top_left = area.top_left - relative.top_left(ORIGIN)
            relative_area = top_left.as_top_left_of(
                area.size
            ).rectangle_area_on_screen
            cut = relative.resource.cut(relative_area)
            relative_drawing = replace(relative, resource=cut)
            res.append(relative_drawing)
        return replace(self, resource=tuple(res))

    @override
    def crop(self, area: RectangleAreaOnScreen) -> Self:
        res: list[ShiftedSprite] = []
        for relative in self.resources:
            top_left = area.top_left - relative.top_left(ORIGIN)
            relative_area = top_left.as_top_left_of(
                area.size
            ).rectangle_area_on_screen
            cropped = relative.resource.crop(relative_area)
            relative_drawing = replace(relative, resource=cropped)
            res.append(relative_drawing)
        return replace(self, resource=tuple(res))

    @override
    def blur(self, radius: BlurRadius) -> Drawing:
        return self.combined_drawing.blur(radius)

    @cached_property
    def combined_drawing(self) -> Drawing:
        return self._drawing_group_on_screen.drawing_on_screen.drawing

    @override
    @cached_property
    def pygame(self) -> Surface:
        return self.combined_drawing.pygame

    @override
    def rotate(self, degree: Degree) -> Self:
        resource = tuple(res.rotate(degree) for res in self.resources)
        return replace(self, resource=resource)

    @cached_property
    def _drawing_group_on_screen(self) -> DrawingGroupOnScreen:
        from nextrpg.drawing.drawing_group_on_screen import DrawingGroupOnScreen

        return DrawingGroupOnScreen(ORIGIN, self)
