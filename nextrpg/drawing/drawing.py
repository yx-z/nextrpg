from dataclasses import dataclass, replace
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Self, override

from pygame import SRCALPHA, Surface
from pygame.image import load
from pygame.transform import flip, gaussian_blur, smoothscale

from nextrpg.config.config import config
from nextrpg.core.cached_decorator import cached
from nextrpg.core.log import Log
from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.drawing.color import TRANSPARENT, Alpha, Color
from nextrpg.drawing.relative_animation_like import RelativeAnimationLike
from nextrpg.geometry.coordinate import ORIGIN, Coordinate
from nextrpg.geometry.dimension import (
    HeightScaling,
    Pixel,
    Size,
    WidthAndHeightScaling,
    WidthScaling,
)
from nextrpg.geometry.padding import Padding
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen

if TYPE_CHECKING:
    from nextrpg.drawing.drawing_on_screen import DrawingOnScreen

log = Log()


@cached(
    lambda: config().drawing.cache_size,
    lambda resource, *args, **kwargs: (
        None if isinstance(resource, Surface) else resource
    ),
)
@dataclass(frozen=True)
class Drawing(AnimationLike):
    resource: Path | Surface
    color_key: Color | Coordinate | None = None
    convert_alpha: bool | None = None
    allow_background_in_debug: bool = True

    @override
    @cached_property
    def drawing(self) -> Drawing:
        return self

    @override
    @cached_property
    def drawings(self) -> tuple[Drawing, ...]:
        return (self,)

    @override
    def __str__(self) -> str:
        if isinstance(self.resource, Surface):
            resource_info = ""
        else:
            resource_info = f", {self.resource}"
        return f"Drawing({self.size}{resource_info})"

    @override
    @cached_property
    def size(self) -> Size:
        return Size(self.surface.width, self.surface.height)

    @cached_property
    def pygame(self) -> Surface:
        if self._debug_surface:
            return self._debug_surface
        return self.surface

    def crop(self, area: RectangleAreaOnScreen) -> Self:
        surface = self.pygame.subsurface(area.pygame)
        return replace(self, resource=surface)

    def trim(self, trim: Padding) -> Self:
        if trim == Padding():
            return self
        area = trim.top_left.anchor(self.size - trim).rectangle_area_on_screen
        return self.crop(area)

    @override
    def alpha(self, alpha: Alpha) -> Self:
        surface = self.surface.copy()
        surface.set_alpha(alpha)
        return replace(self, resource=surface)

    @override
    def drawing_on_screen(self, coordinate: Coordinate) -> DrawingOnScreen:
        from nextrpg.drawing.drawing_on_screen import DrawingOnScreen

        return DrawingOnScreen(coordinate, self)

    @override
    def drawing_on_screens(
        self, top_left: Coordinate
    ) -> tuple[DrawingOnScreen, ...]:
        drawing_on_screen = self.drawing_on_screen(top_left)
        return (drawing_on_screen,)

    def __mul__(
        self, scaling: WidthScaling | HeightScaling | WidthAndHeightScaling
    ) -> Self:
        size = self.size * scaling
        surface = smoothscale(self.surface, size)
        return replace(self, resource=surface)

    @cached_property
    def visible_rectangle_area_on_screen(self) -> RectangleAreaOnScreen:
        rectangle = self.surface.get_bounding_rect()
        coordinate = Coordinate(rectangle.x, rectangle.y)
        size = Size(rectangle.width, rectangle.height)
        return coordinate.anchor(size).rectangle_area_on_screen

    @cached_property
    def rectangle(self) -> RectangleAreaOnScreen:
        return ORIGIN.anchor(self.size).rectangle_area_on_screen

    @cached_property
    def surface(self) -> Surface:
        if isinstance(self.resource, Surface):
            return self.resource

        log.debug(t"Loading {self.resource}")
        res = load(self.resource)
        if not self.color_key:
            if self.convert_alpha is None or self.convert_alpha:
                return res.convert_alpha()
            return res.convert()

        if isinstance(self.color_key, Coordinate):
            color = res.get_at(self.color_key)
            res.set_colorkey(color)
        else:
            res.set_colorkey(self.color_key)

        if self.convert_alpha is None or not self.convert_alpha:
            return res.convert()
        return res.convert_alpha()

    def blur(self, radius: int) -> Self:
        surface = gaussian_blur(self.surface, radius)
        return replace(self, resource=surface)

    @override
    def cut(self, area: RectangleAreaOnScreen) -> Self:
        surface = self.surface.copy()
        surface.fill(TRANSPARENT, (area.top_left, area.size))
        return replace(self, resource=surface)

    @override
    def flip(self, horizontal: bool = False, vertical: bool = False) -> Self:
        surface = flip(self.surface, horizontal, vertical)
        return replace(self, resource=surface)

    def background(
        self,
        color: Color,
        padding: Padding = Padding(),
        border_radius: Pixel = -1,
        width: Pixel = 0,
    ) -> RelativeAnimationLike:
        from nextrpg.drawing.rectangle_drawing import RectangleDrawing

        rect = RectangleDrawing(
            self.size + padding,
            color,
            width,
            border_radius,
            self.allow_background_in_debug,
        )
        return rect.drawing.shift(-padding.top_left_shift)

    @cached_property
    def _debug_surface(self) -> Surface | None:
        if (
            not (debug := config().debug)
            or not (color := debug.drawing_background_color)
            or not self.allow_background_in_debug
        ):
            return None

        size = (self.surface.width, self.surface.height)
        surface = Surface(size, SRCALPHA)
        surface.fill(color)
        surface.blit(self.surface, ORIGIN)
        return surface


def scale_surface(surface: Surface, scaling: float) -> Surface:
    return smoothscale(
        surface, (surface.width * scaling, surface.height * scaling)
    )
