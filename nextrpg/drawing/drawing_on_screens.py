from collections.abc import Iterable
from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, overload, override

from pygame import SRCALPHA, Surface

from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_on_screen import (
    EMPTY_DRAWING_ON_SCREEN,
    DrawingOnScreen,
)
from nextrpg.drawing.sprite_on_screen import (
    SpriteOnScreen,
)
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.directional_offset import DirectionalOffset
from nextrpg.geometry.size import Height, Size, Width


@dataclass(frozen=True)
class DrawingOnScreens(SpriteOnScreen):
    resource: tuple[DrawingOnScreen, ...] = ()

    @cached_property
    def drawing_on_screens(self) -> Self:
        return self

    @overload
    def __add__(
        self, other: SpriteOnScreen | Iterable[SpriteOnScreen]
    ) -> DrawingOnScreens: ...

    @overload
    def __add__(
        self, other: Coordinate | Width | Height | Size | DirectionalOffset
    ) -> Self: ...

    @override
    def __add__(
        self,
        other: (
            Coordinate
            | Width
            | Height
            | Size
            | DirectionalOffset
            | SpriteOnScreen
            | Iterable[SpriteOnScreen]
        ),
    ) -> Self:
        if isinstance(
            other, Coordinate | Width | Height | Size | DirectionalOffset
        ):
            res = tuple(
                drawing_on_screen + other for drawing_on_screen in self.resource
            )
            return replace(self, resource=res)
        return drawing_on_screens(self, other)

    @override
    @cached_property
    def drawing_on_screen(self) -> DrawingOnScreen:
        if not self.resource:
            return EMPTY_DRAWING_ON_SCREEN
        if len(self.resource) == 1:
            return self.resource[0]
        surface = Surface(self.size, SRCALPHA).convert_alpha()
        surface.blits((d - self.top_left).pygame for d in self.resource)
        drawing = Drawing(surface)
        return drawing.drawing_on_screen(self.top_left)

    @override
    @cached_property
    def top_left(self) -> Coordinate:
        min_left = min(d.top_left.left for d in self.resource)
        min_top = min(d.top_left.top for d in self.resource)
        return min_left @ min_top

    @cached_property
    def size(self) -> Size:
        max_left = max(d.bottom_right.left for d in self.resource)
        max_top = max(d.bottom_right.top for d in self.resource)
        width = max_left - self.top_left.left
        height = max_top - self.top_left.top
        return width * height

    def __iter__(self) -> Iterable[DrawingOnScreen]:
        return iter(self.resource)


def drawing_on_screens(
    *resource: SpriteOnScreen | Iterable[SpriteOnScreen],
) -> DrawingOnScreens:
    if isinstance(resource, SpriteOnScreen):
        return resource.drawing_on_screens

    res: list[DrawingOnScreen] = []
    for sprite_on_screen in resource:
        if isinstance(sprite_on_screen, SpriteOnScreen):
            res += sprite_on_screen.drawing_on_screens.resource
        else:
            for s in sprite_on_screen:
                res += s.drawing_on_screens.resource
    return DrawingOnScreens(tuple(res))
