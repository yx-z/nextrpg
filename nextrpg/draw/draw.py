from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from functools import cached_property
from os import PathLike
from typing import Self, override

from pygame import SRCALPHA, Mask, Rect, Surface
from pygame.draw import lines, polygon, rect
from pygame.image import load
from pygame.mask import from_surface
from pygame.transform import smoothscale

from nextrpg.core.cached_decorator import cached
from nextrpg.core.color import BLACK, Alpha, Color
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Pixel, Size
from nextrpg.core.logger import Logger
from nextrpg.global_config.global_config import config

logger = Logger("Draw")


@dataclass(frozen=True, kw_only=True)
class Trim:
    top: Pixel = 0
    left: Pixel = 0
    bottom: Pixel = 0
    right: Pixel = 0


@cached(
    lambda: config().resource.draw_cache_size,
    lambda resource, *_: None if isinstance(resource, Surface) else resource,
)
@dataclass(frozen=True)
class Draw:
    resource: str | PathLike | Surface
    color_key: Color | Coordinate | None = None

    @property
    def width(self) -> Pixel:
        return self._surface.width

    @property
    def height(self) -> Pixel:
        return self._surface.height

    @property
    def size(self) -> Size:
        return Size(self.width, self.height)

    @property
    def pygame(self) -> Surface:
        return self._debug_surface or self._surface

    def crop(self, top_left: Coordinate, size: Size) -> Draw:
        left, top = top_left
        width, height = size
        return Draw(self.pygame.subsurface((left, top, width, height)))

    def trim(self, trim: Trim) -> Draw:
        coord = Coordinate(trim.left, trim.top)
        width = self.width - coord.left - trim.right
        height = self.height - coord.top - trim.bottom
        size = Size(width, height)
        return self.crop(coord, size)

    def set_alpha(self, alpha: Alpha) -> Draw:
        surf = self._surface.copy()
        surf.set_alpha(alpha)
        return Draw(surf)

    def draw_on_screen(self, coord: Coordinate) -> DrawOnScreen:
        return DrawOnScreen(coord, self)

    def __mul__(self, scale: float) -> Draw:
        surf = smoothscale(self._surface, self.size.all_dimension_scale(scale))
        return Draw(surf)

    @cached_property
    def _visible_rectangle(self) -> RectangleOnScreen:
        rectangle = self._surface.get_bounding_rect()
        coord = Coordinate(rectangle.x, rectangle.y)
        size = Size(rectangle.width, rectangle.height)
        return RectangleOnScreen(coord, size)

    @cached_property
    def _debug_surface(self) -> Surface | None:
        if not config().debug or not (
            color := config().debug.draw_background_color
        ):
            return None

        surface = Surface(self.size, SRCALPHA)
        surface.fill(color)
        surface.blit(self._surface, (0, 0))
        return surface

    @cached_property
    def _surface(self) -> Surface:
        if isinstance(self.resource, Surface):
            res = self.resource
        else:
            logger.debug(t"Loading {self.resource}")
            res = load(self.resource).convert_alpha()

        if self.color_key:
            if isinstance(self.color_key, Coordinate):
                color = res.get_at(self.color_key)
                res.set_colorkey(color)
            else:
                res.set_colorkey(self.color_key)
        return res


@dataclass(frozen=True)
class DrawOnScreen:
    top_left: Coordinate
    draw: Draw

    @property
    def rectangle_on_screen(self) -> RectangleOnScreen:
        return RectangleOnScreen(self.top_left, self.draw.size)

    @cached_property
    def visible_rectangle_on_screen(self) -> RectangleOnScreen:
        coord = self.draw._visible_rectangle.top_left
        size = self.draw._visible_rectangle.size
        return RectangleOnScreen(self.top_left + coord, size)

    @property
    def pygame(self) -> tuple[Surface, Coordinate]:
        return self.draw.pygame, self.top_left

    def __add__(self, coord: Coordinate) -> DrawOnScreen:
        return DrawOnScreen(self.top_left + coord, self.draw)

    def __sub__(self, coord: Coordinate) -> DrawOnScreen:
        return self + -coord

    def set_alpha(self, alpha: Alpha) -> DrawOnScreen:
        return DrawOnScreen(self.top_left, self.draw.set_alpha(alpha))


class PolygonDraw:
    def __init__(self, points: tuple[Coordinate, ...], color: Color) -> None:
        surf = _draw_polygon(points, _fill_polygon(color))
        _set_resource_and_color_key(self, surf)


@dataclass(frozen=True)
class PolygonOnScreen:

    points: tuple[Coordinate, ...]
    closed: bool = True

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

    @cached_property
    def _mask(self) -> Mask:
        return from_surface(self.fill(BLACK).draw.pygame)

    def fill(self, color: Color) -> DrawOnScreen:
        return self._draw(_fill_polygon(color))

    def line(
        self, color: Color, stroke_width: Pixel | None = None
    ) -> DrawOnScreen:
        if stroke_width is None:
            stroke = config().draw_on_screen.stroke_width
        else:
            stroke = stroke_width

        def _line(surface: Surface, points: tuple[Coordinate, ...]) -> None:
            lines(surface, color, self.closed, points, stroke)

        return self._draw(_line)

    def collide(self, poly: PolygonOnScreen) -> bool:
        if not self.bounding_rectangle.collide(poly.bounding_rectangle):
            return False
        offset = (
            self.bounding_rectangle.top_left - poly.bounding_rectangle.top_left
        )
        return bool(self._mask.overlap(poly._mask, offset))

    def __contains__(self, coordinate: Coordinate) -> bool:
        x, y = coordinate - self.bounding_rectangle.top_left
        width, height = self._mask.get_size()
        if 0 <= x < width and 0 <= y < height:
            return bool(self._mask.get_at((x, y)))
        return False

    def _draw(
        self, method: Callable[[Surface, tuple[Coordinate, ...]], None]
    ) -> DrawOnScreen:
        surf = _draw_polygon(self.points, method, self.bounding_rectangle)
        return DrawOnScreen(self.bounding_rectangle.top_left, Draw(surf))

    def __add__(self, coordinate: Coordinate) -> Self:
        points = tuple(t + coordinate for t in self.points)
        return replace(self, points=points)

    def __sub__(self, coordinate: Coordinate) -> Self:
        return self + -coordinate


class RectangleDraw(Draw):
    def __init__(
        self, size: Size, color: Color, border_radius: Pixel | None = None
    ) -> None:
        surface = Surface(size, SRCALPHA)
        rectangle = Rect(Coordinate(0, 0), size)
        rect(surface, color, rectangle, border_radius=border_radius or -1)
        _set_resource_and_color_key(self, surface)


class RectangleOnScreen(PolygonOnScreen):

    def __init__(self, top_left: Coordinate, size: Size) -> None:
        self.top_left = top_left
        self.size = size

    @property
    def left(self) -> Pixel:
        return self.top_left.left

    @property
    def right(self) -> Pixel:
        return self.left + self.size.width

    @property
    def top(self) -> Pixel:
        return self.top_left.top

    @property
    def bottom(self) -> Pixel:
        return self.top + self.size.height

    @property
    def top_right(self) -> Coordinate:
        return Coordinate(self.right, self.top)

    @property
    def bottom_left(self) -> Coordinate:
        return Coordinate(self.left, self.bottom)

    @property
    def bottom_right(self) -> Coordinate:
        return Coordinate(self.right, self.bottom)

    @property
    def top_center(self) -> Coordinate:
        return Coordinate(self.left + self.size.width / 2, self.top)

    @property
    def bottom_center(self) -> Coordinate:
        return Coordinate(self.left + self.size.width / 2, self.bottom)

    @property
    def center_left(self) -> Coordinate:
        return Coordinate(self.left, self.top + self.size.height / 2)

    @property
    def center_right(self) -> Coordinate:
        return Coordinate(self.right, self.top + self.size.height / 2)

    @property
    def center(self) -> Coordinate:
        width, height = self.size
        return Coordinate(self.left + width / 2, self.top + height / 2)

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

    @override
    def __add__(self, coordinate: Coordinate) -> RectangleOnScreen:
        return RectangleOnScreen(self.top_left + coordinate, self.size)

    def fill(
        self, color: Color, border_radius: Pixel | None = None
    ) -> DrawOnScreen:
        return DrawOnScreen(
            self.top_left, RectangleDraw(self.size, color, border_radius)
        )


def _bounding_rectangle(points: tuple[Coordinate, ...]) -> RectangleOnScreen:
    min_x = min(c.left for c in points)
    min_y = min(c.top for c in points)
    max_x = max(c.left for c in points)
    max_y = max(c.top for c in points)
    coord = Coordinate(min_x, min_y)
    size = Size(max_x - min_x, max_y - min_y)
    return RectangleOnScreen(coord, size)


def _draw_polygon(
    points: tuple[Coordinate, ...],
    method: Callable[[Surface, tuple[Coordinate, ...]], None],
    bounding_rectangle: RectangleOnScreen | None = None,
) -> Surface:
    bounding_rectangle = bounding_rectangle or _bounding_rectangle(points)
    surf = Surface(bounding_rectangle.size, SRCALPHA)
    negated = tuple(p - bounding_rectangle.top_left for p in points)
    method(surf, negated)
    return surf


def _set_resource_and_color_key[T](self: T, surface: Surface) -> None:
    object.__setattr__(self, "resource", surface)
    object.__setattr__(self, "color_key", None)


def _fill_polygon(
    color: Color,
) -> Callable[[Surface, tuple[Coordinate, ...]], None]:
    def fill(surface: Surface, points: tuple[Coordinate, ...]) -> None:
        polygon(surface, color, points)

    return fill
