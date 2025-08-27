from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from pygame import SRCALPHA, Surface
from pygame.image import load
from pygame.transform import flip, scale, smoothscale

from nextrpg.core.cached_decorator import cached
from nextrpg.core.color import TRANSPARENT, Alpha, Color
from nextrpg.core.coordinate import ORIGIN, Coordinate
from nextrpg.core.dimension import (
    HeightScaling,
    Pixel,
    Size,
    WidthAndHeightScaling,
    WidthScaling,
)
from nextrpg.core.log import Log
from nextrpg.core.sizable import Sizable
from nextrpg.draw.drawing_trim import DrawingTrim
from nextrpg.global_config.global_config import config

if TYPE_CHECKING:
    from nextrpg.draw.drawing_on_screen import DrawingOnScreen
    from nextrpg.draw.rectangle_area_on_screen import RectangleAreaOnScreen

log = Log()


@cached(
    lambda: config().drawing.cache_size,
    lambda resource, *args, **kwargs: (
        None if isinstance(resource, Surface) else resource
    ),
)
@dataclass(frozen=True)
class Drawing(Sizable):
    resource: str | Path | Surface
    color_key: Color | Coordinate | None = None
    convert_alpha: bool | None = None
    allow_background_in_debug: bool = True

    @property
    def size(self) -> Size:
        return Size(self.surface.width, self.surface.height)

    @property
    def pygame(self) -> Surface:
        if self._debug_surface:
            return self._debug_surface
        return self.surface

    def cut(self, top_left: Coordinate, size: Size) -> Drawing:
        surface = self.surface.convert_alpha()
        surface.fill(TRANSPARENT, (top_left, size))
        return replace(self, resource=surface)

    def flip(self, horizontal: bool = False, vertical: bool = False) -> Drawing:
        surface = flip(self.surface, horizontal, vertical)
        return replace(self, resource=surface)

    def crop(self, top_left: Coordinate, size: Size) -> Drawing:
        surface = self.pygame.subsurface((top_left, size))
        return replace(self, resource=surface)

    def trim(self, drawing_trim: DrawingTrim) -> Drawing:
        coordinate = Coordinate(drawing_trim.left, drawing_trim.top)
        width = self.surface.width - drawing_trim.left - drawing_trim.right
        height = self.surface.height - drawing_trim.top - drawing_trim.bottom
        size = Size(width, height)
        return self.crop(coordinate, size)

    def set_alpha(self, alpha: Alpha) -> Drawing:
        surface = self.surface.copy()
        surface.set_alpha(alpha)
        return replace(self, resource=surface)

    def drawing_on_screen(self, coordinate: Coordinate) -> DrawingOnScreen:
        from nextrpg.draw.drawing_on_screen import DrawingOnScreen

        return DrawingOnScreen(coordinate, self)

    def __mul__(
        self,
        scaling: (
            int | float | WidthScaling | HeightScaling | WidthAndHeightScaling
        ),
        smooth: bool | None = None,
    ) -> Drawing:
        if isinstance(scaling, int | float):
            scaling = WidthAndHeightScaling(scaling)
        size = self.size * scaling
        scale_fun = _get_scale_fun(smooth)
        surface = scale_fun(self.surface, size)
        return replace(self, resource=surface)

    def scale_fast(
        self, scaling: int | float, smooth: bool | None = None
    ) -> Drawing:
        width, height = self.size
        size = (width * scaling, height * scaling)
        scale_fun = _get_scale_fun(smooth)
        surface = scale_fun(self.surface, size)
        return replace(self, resource=surface)

    @cached_property
    def visible_rectangle_area_on_screen(self) -> RectangleAreaOnScreen:
        from nextrpg.draw.rectangle_area_on_screen import RectangleAreaOnScreen

        rectangle = self.surface.get_bounding_rect()
        coordinate = Coordinate(rectangle.x, rectangle.y)
        size = Size(rectangle.width, rectangle.height)
        return RectangleAreaOnScreen(coordinate, size)

    @property
    def rectangle(self) -> RectangleAreaOnScreen:
        from nextrpg.draw.polygon_area_on_screen import RectangleAreaOnScreen

        return RectangleAreaOnScreen(ORIGIN, self.size)

    @property
    def top_left(self) -> Coordinate:
        return ORIGIN

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


def _get_scale_fun(
    smooth: bool | None,
) -> Callable[[Surface, Size | tuple[Pixel, Pixel]], Surface]:
    if smooth is None:
        smooth = config().drawing.smooth_line
    if smooth:
        return smoothscale
    return scale
