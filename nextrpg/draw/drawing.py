from __future__ import annotations

from abc import ABC
from collections.abc import Callable
from dataclasses import KW_ONLY, dataclass
from functools import cached_property
from pathlib import Path
from typing import override

from pygame import SRCALPHA, Mask, Rect, Surface
from pygame.draw import lines, polygon, rect
from pygame.image import load
from pygame.mask import from_surface
from pygame.transform import smoothscale

from nextrpg.core.cached_decorator import cached
from nextrpg.core.color import BLACK, TRANSPARENT, Alpha, Color
from nextrpg.core.coordinate import ORIGIN, Coordinate
from nextrpg.core.dataclass_with_init import (
    dataclass_with_init,
    default,
    not_constructor_below,
)
from nextrpg.core.dimension import (
    Height,
    Pixel,
    Size,
    Width,
    WidthAndHeightScaling,
)
from nextrpg.core.log import Log
from nextrpg.core.sizeable import Sizeable
from nextrpg.global_config.global_config import config

log = Log()


@dataclass(frozen=True, kw_only=True)
class Trim:
    top: Pixel = 0
    left: Pixel = 0
    bottom: Pixel = 0
    right: Pixel = 0


@cached(
    lambda: config().drawing.cache_size,
    lambda resource, *_: None if isinstance(resource, Surface) else resource,
)
@dataclass(frozen=True)
class Drawing(Sizeable):
    resource: str | Path | Surface
    color_key: Color | Coordinate | None = None

    @property
    def size(self) -> Size:
        return Size(self.surface.width, self.surface.height)

    @property
    def pygame(self) -> Surface:
        return self._debug_surface or self.surface

    def crop(self, top_left: Coordinate, size: Size) -> Drawing:
        return Drawing(self.pygame.subsurface((top_left.tuple, size.tuple)))

    def trim(self, trim: Trim) -> Drawing:
        coordinate = Coordinate(trim.left, trim.top)
        width = self.width - trim.left - trim.right
        height = self.height - trim.top - trim.bottom
        size = Size(width, height)
        return self.crop(coordinate, size)

    def set_alpha(self, alpha: Alpha) -> Drawing:
        surf = self.surface.copy()
        surf.set_alpha(alpha)
        return Drawing(surf)

    def drawing_on_screen(self, coordinate: Coordinate) -> DrawingOnScreen:
        return DrawingOnScreen(coordinate, self)

    def __mul__(self, scaling: int | float | WidthAndHeightScaling) -> Drawing:
        size = self.size * WidthAndHeightScaling(scaling)
        surf = smoothscale(self.surface, size.tuple)
        return Drawing(surf)

    @cached_property
    def visible_rectangle(self) -> RectangleOnScreen:
        rectangle = self.surface.get_bounding_rect()
        coordinate = Coordinate(rectangle.x, rectangle.y)
        size = Size(rectangle.width, rectangle.height)
        return RectangleOnScreen(coordinate, size)

    @property
    def rectangle(self) -> RectangleOnScreen:
        return RectangleOnScreen(ORIGIN, self.size)

    @property
    def top_left(self) -> Coordinate:
        return ORIGIN

    @cached_property
    def surface(self) -> Surface:
        if isinstance(self.resource, Surface):
            res = self.resource
        else:
            log.debug(t"Loading {self.resource}")
            res = load(self.resource).convert_alpha()

        if self.color_key:
            if isinstance(self.color_key, Coordinate):
                color = res.get_at(self.color_key.tuple)
                res.set_colorkey(color)
            else:
                res.set_colorkey(self.color_key)
        return res

    @cached_property
    def _debug_surface(self) -> Surface | None:
        if not (debug := config().debug) or not (
            color := debug.drawing_background_color
        ):
            return None

        surface = Surface(self.size.tuple, SRCALPHA)
        surface.fill(color.tuple)
        surface.blit(self.surface, (0, 0))
        return surface


@dataclass(frozen=True)
class DrawingOnScreen(Sizeable):
    top_left: Coordinate
    draw: Drawing

    @property
    def rectangle_on_screen(self) -> RectangleOnScreen:
        return RectangleOnScreen(self.top_left, self.draw.size)

    @cached_property
    def visible_rectangle_on_screen(self) -> RectangleOnScreen:
        shift = self.draw.visible_rectangle.top_left
        size = self.draw.visible_rectangle.size
        return RectangleOnScreen(self.top_left + shift, size)

    @property
    def pygame(self) -> tuple[Surface, tuple[Pixel, Pixel]]:
        return self.draw.pygame, self.top_left.tuple

    def set_alpha(self, alpha: Alpha) -> DrawingOnScreen:
        return DrawingOnScreen(self.top_left, self.draw.set_alpha(alpha))

    @property
    def size(self) -> Size:
        return self.draw.size

    def __add__(
        self, other: Coordinate | Size | Width | Height
    ) -> DrawingOnScreen:
        return DrawingOnScreen(self.top_left + other, self.draw)

    def __sub__(
        self, other: Coordinate | Size | Width | Height
    ) -> DrawingOnScreen:
        return self + -other


class TransparentDrawing(Drawing, ABC):
    color: Color

    @property
    def transparent(self) -> bool:
        return self.color == TRANSPARENT

    @override
    @cached_property
    def surface(self) -> Surface:
        if self.transparent:
            return Surface((0, 0))
        return super().surface

    @override
    @cached_property
    def size(self) -> Size:
        if self.transparent:
            return Drawing(self.resource).size
        return super().size


class PolygonDrawing(TransparentDrawing):
    def __init__(self, points: tuple[Coordinate, ...], color: Color) -> None:
        surf = _draw_polygon(points, _fill_polygon(color))
        _set_resource_color_and_color_key(self, surf, color)


@dataclass_with_init(frozen=True)
class PolygonOnScreen(Sizeable):
    points: tuple[Coordinate, ...]
    closed: bool = True
    _: KW_ONLY = not_constructor_below()
    top_left: Coordinate = default(
        lambda self: self.bounding_rectangle.top_left
    )
    size: Size = default(lambda self: self.bounding_rectangle.size)

    @cached_property
    def length(self) -> Pixel:
        length = sum(
            p.distance(np) for p, np in zip(self.points, self.points[1:])
        )
        if self.closed:
            return length + self.points[0].distance(self.points[-1])
        return length

    @cached_property
    def bounding_rectangle(self) -> RectangleOnScreen:
        return _bounding_rectangle(self.points)

    def fill(self, color: Color) -> DrawingOnScreen:
        return self._drawing_on_screen(_fill_polygon(color))

    def line(
        self, color: Color, stroke_width: Pixel | None = None
    ) -> DrawingOnScreen:
        if stroke_width is None:
            stroke = config().drawing.stroke_thickness
        else:
            stroke = stroke_width

        def _line(surface: Surface, points: tuple[Coordinate, ...]) -> None:
            point_tuples = tuple(p.tuple for p in points)
            lines(surface, color.tuple, self.closed, point_tuples, stroke)

        return self._drawing_on_screen(_line)

    def collide(self, poly: PolygonOnScreen) -> bool:
        if not self.bounding_rectangle.collide(poly.bounding_rectangle):
            return False
        offset = (
            self.bounding_rectangle.top_left - poly.bounding_rectangle.top_left
        )
        return bool(self._mask.overlap(poly._mask, offset.tuple))

    def __contains__(self, coordinate: Coordinate) -> bool:
        x, y = (coordinate - self.bounding_rectangle.top_left).tuple
        width, height = self._mask.get_size()
        if 0 <= x < width and 0 <= y < height:
            return bool(self._mask.get_at((x, y)))
        return False

    def __add__(
        self, other: Coordinate | Size | Width | Height
    ) -> PolygonOnScreen:
        points = tuple(p + other for p in self.points)
        return PolygonOnScreen(points, self.closed)

    def __sub__(
        self, other: Coordinate | Size | Width | Height
    ) -> PolygonOnScreen:
        return self + -other

    @cached_property
    def _mask(self) -> Mask:
        return from_surface(self.fill(BLACK).draw.pygame)

    def _drawing_on_screen(
        self, method: Callable[[Surface, tuple[Coordinate, ...]], None]
    ) -> DrawingOnScreen:
        surf = _draw_polygon(self.points, method, self.bounding_rectangle)
        return DrawingOnScreen(self.bounding_rectangle.top_left, Drawing(surf))


class RectangleDrawing(TransparentDrawing):
    def __init__(
        self, size: Size, color: Color, border_radius: Pixel | None = None
    ) -> None:
        surface = Surface(size.tuple, SRCALPHA)
        rectangle = Rect(ORIGIN.tuple, size.tuple)
        rect(surface, color.tuple, rectangle, border_radius=border_radius or -1)
        _set_resource_color_and_color_key(self, surface, color)


class RectangleOnScreen(PolygonOnScreen):
    def __init__(self, top_left: Coordinate, size: Size) -> None:
        object.__setattr__(self, "top_left", top_left)
        object.__setattr__(self, "size", size)

    @property
    def points(self) -> tuple[Coordinate, ...]:
        return (
            self.top_left,
            self.top_right,
            self.bottom_right,
            self.bottom_left,
        )

    @override
    def collide(self, poly: PolygonOnScreen) -> bool:
        if not isinstance(poly, RectangleOnScreen):
            return super().collide(poly)

        return (
            self.top_left.left < poly.top_right.left
            and self.top_right.left > poly.top_left.left
            and self.top_left.top < poly.bottom_right.top
            and self.bottom_right.top > poly.top_left.top
        )

    @override
    def __contains__(self, coordinate: Coordinate) -> bool:
        return (
            self.left < coordinate.left < self.right
            and self.top < coordinate.top < self.bottom
        )

    def __add__(
        self, other: Coordinate | Size | Width | Height
    ) -> RectangleOnScreen:
        return RectangleOnScreen(self.top_left + other, self.size)

    def __sub__(
        self, other: Coordinate | Size | Width | Height
    ) -> RectangleOnScreen:
        return RectangleOnScreen(self.top_left - other, self.size)

    def fill(
        self, color: Color, border_radius: Pixel | None = None
    ) -> DrawingOnScreen:
        return DrawingOnScreen(
            self.top_left, RectangleDrawing(self.size, color, border_radius)
        )


@dataclass(frozen=True)
class SizedDrawOnScreens(Sizeable):
    draw_on_screens: tuple[DrawingOnScreen, ...]

    @cached_property
    def top_left(self) -> Coordinate:
        min_left = min(d.top_left.left for d in self.draw_on_screens)
        min_top = min(d.top_left.top for d in self.draw_on_screens)
        return Coordinate(min_left, min_top)

    @cached_property
    def size(self) -> Size:
        min_left = min(d.top_left.left for d in self.draw_on_screens)
        min_top = min(d.top_left.top for d in self.draw_on_screens)
        max_left = max(d.bottom_right.left for d in self.draw_on_screens)
        max_top = max(d.bottom_right.top for d in self.draw_on_screens)
        width = max_left - min_left
        height = max_top - min_top
        return Size(width, height)


def _bounding_rectangle(points: tuple[Coordinate, ...]) -> RectangleOnScreen:
    min_x = min(c.left for c in points)
    min_y = min(c.top for c in points)
    max_x = max(c.left for c in points)
    max_y = max(c.top for c in points)
    coordinate = Coordinate(min_x, min_y)
    size = Size(max_x - min_x, max_y - min_y)
    return RectangleOnScreen(coordinate, size)


def _draw_polygon(
    points: tuple[Coordinate, ...],
    method: Callable[[Surface, tuple[Coordinate, ...]], None],
    bounding_rectangle: RectangleOnScreen | None = None,
) -> Surface:
    bounding_rectangle = bounding_rectangle or _bounding_rectangle(points)
    surf = Surface(bounding_rectangle.size.tuple, SRCALPHA)
    negated = tuple(p - bounding_rectangle.top_left for p in points)
    method(surf, negated)
    return surf


def _set_resource_color_and_color_key[T](
    self: T, surface: Surface, color: Color
) -> None:
    object.__setattr__(self, "resource", surface)
    object.__setattr__(self, "color", color)
    object.__setattr__(self, "color_key", None)


def _fill_polygon(
    color: Color,
) -> Callable[[Surface, tuple[Coordinate, ...]], None]:
    def fill(surface: Surface, points: tuple[Coordinate, ...]) -> None:
        point_tuples = tuple(p.tuple for p in points)
        polygon(surface, color.tuple, point_tuples)

    return fill
