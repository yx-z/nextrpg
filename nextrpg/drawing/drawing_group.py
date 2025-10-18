from dataclasses import dataclass, replace
from functools import cached_property
from typing import TYPE_CHECKING, Self, override

from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.drawing.color import Alpha
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.relative_animation_like import RelativeAnimationLike
from nextrpg.geometry.coordinate import ORIGIN, Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen

if TYPE_CHECKING:
    from nextrpg.drawing.drawing_group_on_screen import DrawingGroupOnScreen


@dataclass(frozen=True)
class DrawingGroup(AnimationLike):
    resource: RelativeAnimationLike | tuple[RelativeAnimationLike, ...]

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
        if isinstance(self.resource, tuple):
            return self.resource
        return (self.resource,)

    @override
    def alpha(self, alpha: Alpha) -> Drawing | DrawingGroup:
        resources = tuple(res.alpha(alpha) for res in self.resources)
        return replace(self, resource=resources)

    @override
    @cached_property
    def drawing(self) -> DrawingGroup:
        return self

    @override
    @cached_property
    def drawings(self) -> tuple[Drawing, ...]:
        res: list[Drawing] = []
        for relative in self.resources:
            if isinstance(relative.resource, Drawing):
                res.append(relative.resource)
            else:
                res += relative.resource.drawings
        return tuple(res)

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
            drawing = relative.resource.cut(relative_area)
            relative_drawing = replace(relative, drawing=drawing)
            res.append(relative_drawing)
        return replace(self, resource=tuple(res))

    @cached_property
    def _drawing_group_on_screen(self) -> DrawingGroupOnScreen:
        from nextrpg.drawing.drawing_group_on_screen import DrawingGroupOnScreen

        return DrawingGroupOnScreen(ORIGIN, self)
