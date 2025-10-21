from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import TYPE_CHECKING, Any, Self, override

from nextrpg.core.metadata import HasMetadata
from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.drawing.color import Alpha
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.relative_animation_like import (
    RelativeAnimationLike,
    relative_animation_likes,
)
from nextrpg.geometry.coordinate import ORIGIN, Coordinate
from nextrpg.geometry.dimension import HeightScaling, Size, WidthScaling
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen

if TYPE_CHECKING:
    from nextrpg.drawing.drawing_group_on_screen import DrawingGroupOnScreen


@dataclass(frozen=True)
class DrawingGroup(AnimationLike, HasMetadata):
    resource: (
        AnimationLike
        | RelativeAnimationLike
        | tuple[AnimationLike | RelativeAnimationLike, ...]
    )
    metadata: dict[str, Any] = field(default_factory=dict)

    @override
    @cached_property
    def is_complete(self) -> bool:
        return all(res.is_complete for res in self.resources)

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        resources = tuple(res.tick(time_delta) for res in self.resources)
        return replace(self, resource=resources)

    @cached_property
    def resources(self) -> tuple[RelativeAnimationLike, ...]:
        return relative_animation_likes(self.resource)

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
        self, origin: Coordinate
    ) -> tuple[DrawingOnScreen, ...]:
        return self.group_on_screen(origin).drawing_on_screens

    def group_on_screen(self, origin: Coordinate) -> DrawingGroupOnScreen:
        from nextrpg.drawing.drawing_group_on_screen import DrawingGroupOnScreen

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
        res: list[RelativeAnimationLike] = []
        for relative in self.resources:
            top_left = area.top_left - relative.top_left(ORIGIN)
            relative_area = top_left.anchor(area.size).rectangle_area_on_screen
            resource = relative.resource.cut(relative_area)
            relative_drawing = replace(relative, resource=resource)
            res.append(relative_drawing)
        return replace(self, resource=tuple(res))

    @cached_property
    def _drawing_group_on_screen(self) -> DrawingGroupOnScreen:
        from nextrpg.drawing.drawing_group_on_screen import DrawingGroupOnScreen

        return DrawingGroupOnScreen(ORIGIN, self)
