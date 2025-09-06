from __future__ import annotations

from dataclasses import dataclass, replace
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Self

from pygame import SRCALPHA, Surface
from pygame.image import load
from pygame.transform import flip, gaussian_blur, smoothscale

from nextrpg.config.config import config
from nextrpg.core.cached_decorator import cached
from nextrpg.core.log import Log
from nextrpg.draw.anchor import Anchor
from nextrpg.draw.color import TRANSPARENT, Alpha, Color
from nextrpg.draw.drawing_trim import DrawingTrim
from nextrpg.geometry.coordinate import ORIGIN, Coordinate
from nextrpg.geometry.dimension import (
    ZERO_SIZE,
    HeightScaling,
    Size,
    WidthAndHeightScaling,
    WidthScaling,
)
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.geometry.sizable import Sizable

if TYPE_CHECKING:
    from nextrpg.draw.drawing_on_screen import DrawingOnScreen
    from nextrpg.draw.relative_drawing import RelativeDrawing

log = Log()


@cached(
    lambda: config().drawing.cache_size,
    lambda resource, *args, **kwargs: (
        None if isinstance(resource, Surface) else resource
    ),
)
@dataclass(frozen=True)
class Drawing(Sizable):
    resource: Path | Surface
    color_key: Color | Coordinate | None = None
    convert_alpha: bool | None = None
    allow_background_in_debug: bool = True

    @property
    def no_shift(self) -> RelativeDrawing:
        return self.shift(ZERO_SIZE)

    def shift(
        self, shift: Size, anchor: Anchor = Anchor.TOP_LEFT
    ) -> RelativeDrawing:
        from nextrpg.draw.relative_drawing import RelativeDrawing

        return RelativeDrawing(self, shift, anchor)

    @property
    def size(self) -> Size:
        return Size(self.surface.width, self.surface.height)

    @cached_property
    def pygame(self) -> Surface:
        if self._debug_surface:
            return self._debug_surface
        return self.surface

    def cut(self, area: RectangleAreaOnScreen) -> Self:
        surface = self.surface.copy()
        surface.fill(TRANSPARENT, (area.top_left, area.size))
        return replace(self, resource=surface)

    def flip(self, horizontal: bool = False, vertical: bool = False) -> Self:
        surface = flip(self.surface, horizontal, vertical)
        return replace(self, resource=surface)

    def crop(self, area: RectangleAreaOnScreen) -> Self:
        surface = self.pygame.subsurface(area.pygame)
        return replace(self, resource=surface)

    def trim(self, drawing_trim: DrawingTrim) -> Self:
        coordinate = (drawing_trim.left * drawing_trim.top).coordinate
        width = self.width - drawing_trim.left - drawing_trim.right
        height = self.height - drawing_trim.top - drawing_trim.bottom
        area = coordinate.anchor(width * height).rectangle_area_on_screen
        return self.crop(area)

    def set_alpha(self, alpha: Alpha) -> Self:
        surface = self.surface.copy()
        surface.set_alpha(alpha)
        return replace(self, resource=surface)

    def drawing_on_screen(self, coordinate: Coordinate) -> DrawingOnScreen:
        from nextrpg.draw.drawing_on_screen import DrawingOnScreen

        return DrawingOnScreen(coordinate, self)

    def __mul__(
        self, scaling: WidthScaling | HeightScaling | WidthAndHeightScaling
    ) -> Self:
        size = self.size * scaling
        surface = smoothscale(self.surface, size)
        return replace(self, resource=surface)

    def scale_fast(self, scaling: float) -> Drawing:
        return Drawing(
            smoothscale(
                self.surface,
                (self.surface.width * scaling, self.surface.height * scaling),
            )
        )

    @cached_property
    def visible_rectangle_area_on_screen(self) -> RectangleAreaOnScreen:
        rectangle = self.surface.get_bounding_rect()
        coordinate = Coordinate(rectangle.x, rectangle.y)
        size = Size(rectangle.width, rectangle.height)
        return coordinate.anchor(size).rectangle_area_on_screen

    @property
    def rectangle(self) -> RectangleAreaOnScreen:
        return ORIGIN.anchor(self.size).rectangle_area_on_screen

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

    def blur(self, radius: int | float) -> Self:
        surface = gaussian_blur(self.surface, radius)
        return replace(self, resource=surface)

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
