"""
Drawable on screen.
"""

from dataclasses import dataclass
from functools import cached_property
from math import ceil
from os import PathLike
from typing import Self

from pygame import Mask, SRCALPHA, Surface
from pygame.draw import polygon
from pygame.image import load
from pygame.mask import from_surface

from nextrpg.config import config
from nextrpg.coordinate import Coordinate
from nextrpg.core import Alpha, Pixel, Rgba, Size
from nextrpg.logger import FROM_CONFIG, Logger
from nextrpg.model import cached

logger = Logger("Draw")


@cached(
    lambda: config().resource.drawing_cache_size,
    lambda resource: None if isinstance(resource, Surface) else resource,
)
@dataclass(frozen=True)
class Drawing:
    """
    Represents a drawable element and provides methods for accessing its size
    and dimensions.

    This class loads a surface from a file or directly accepts a
    `pygame.Surface` as input.
    It provides properties to access surface dimensions and size and methods to
    crop and scale the surface.

    Arguments:
        `resource`: A path to a file containing the drawing resource,
            or a `pygame.Surface` object.
    """

    resource: str | PathLike | Surface

    @property
    def width(self) -> Pixel:
        """
        Gets the width of the surface.

        Returns:
            `Pixel`: The width of the surface in pixel measurement.
        """
        return self._surface.get_width()

    @property
    def height(self) -> Pixel:
        """
        Gets the height of the surface.

        Returns:
            `Pixel`: The height of the surface in pixel measurement.
        """
        return self._surface.get_height()

    @property
    def size(self) -> Size:
        """
        Gets the size of an object as a combination of its width and height

        Returns:
            `Size`: A Size object containing the width and height of the object.
        """
        return Size(self.width, self.height)

    @property
    def pygame(self) -> Surface:
        """
        Gets the current `pygame.Surface` for the object.

        Returns:
            `pygame.Surface`: The underlying `pygame.Surface`.
        """
        return self._debug_surface or self._surface

    def crop(self, top_left: Coordinate, size: Size) -> Self:
        """
        Crops a rectangular portion of the drawing specified by the
        top-left corner and the size.

        The method extracts a subsection of the drawing based on the provided
        coordinates and dimensions and returns a new `Drawing` instance.
        The original drawing remains unchanged.

        Arguments:
            `top_left`: The top-left coordinate of the rectangle to be cropped.

            `size`: The width and height of the rectangle to be cropped.

        Returns:
            `Drawing`: A new `Drawing` instance representing the cropped area.
        """
        left, top = top_left
        width, height = size
        return Drawing(self._surface.subsurface((left, top, width, height)))

    def set_alpha(self, alpha: Alpha) -> Self:
        """
        Creates a new `Drawing` with the specified alpha value.

        Arguments:
            `alpha`: The new alpha value.

        Returns:
            `Drawing`: A new `Drawing` with the specified alpha value.
        """
        surface = self._surface.copy()
        surface.set_alpha(alpha)
        return Drawing(surface)

    @cached_property
    def visible_rectangle(self) -> Rectangle:
        visible = [
            Coordinate(x, y)
            for x in range(ceil(self.width))
            for y in range(ceil(self.height))
            if self._surface.get_at((x, y)).a
        ]
        if not visible:
            return Rectangle(Coordinate(0, 0), Size(0, 0))

        min_x = min(c.left for c in visible)
        min_y = min(c.top for c in visible)
        max_x = max(c.left for c in visible)
        max_y = max(c.top for c in visible)
        return Rectangle(
            Coordinate(min_x, min_y), Size(max_x - min_x, max_y - min_y)
        )

    @cached_property
    def _debug_surface(self) -> Surface | None:
        if debug := config().debug:
            surface = Surface(self.size, SRCALPHA)
            surface.fill(debug.drawing_background_color)
            surface.blit(self._surface, (0, 0))
            return surface
        return None

    @cached_property
    def _surface(self) -> Surface:
        if isinstance(self.resource, Surface):
            return self.resource
        logger.debug(t"Loading {self.resource}", duration=FROM_CONFIG)
        return load(self.resource).convert_alpha()


@dataclass(frozen=True)
class DrawOnScreen:
    """
    Represents a drawable element positioned on the screen with its coordinates.

    This immutable class combines a drawing with its position and provides
    properties to access various coordinates and dimensions of the drawing
    on the screen.

    Attributes:
        `top_left`: The top-left position of the drawing on the screen.

        `drawing`: The drawable element to be displayed on the screen.
    """

    top_left: Coordinate
    drawing: Drawing

    @property
    def rectangle(self) -> Rectangle:
        """
        Gets the rectangular bounds of the drawing on screen.

        Returns:
            `Rectangle`: A rectangle defining the drawing's position and size
            on screen.
        """
        return Rectangle(self.top_left, self.drawing.size)

    @cached_property
    def visible_rectangle(self) -> Rectangle:
        """
        Calculate the actual visible bounds of the drawing,
        ignoring transparent pixels.

        Returns:
            `Rectangle`: A rectangle defining only the visible (non-transparent)
            portion of the drawing on screen.
        """
        return self.drawing.visible_rectangle.shift(self.top_left)

    @property
    def pygame(self) -> tuple[Surface, Coordinate]:
        """
        Gets the pygame surface and coordinate tuple for rendering.

        Returns:
            `tuple[pygame.Surface, tuple[float, float]]`:
                A tuple containing the `pygame.Surface` and a tuple of the left
                and top coordinates (x, y).
        """
        return self.drawing.pygame, self.top_left

    def shift(self, coord: Coordinate) -> Self:
        """
        Shift the drawing by the specified coordinate.

        Arguments:
            `coord`: The coordinate to shift the drawing by.

        Returns:
            `DrawOnScreen`: A new `DrawOnScreen` shifted by the coordinate.
        """
        return DrawOnScreen(self.top_left.shift(coord), self.drawing)


@dataclass(frozen=True)
class Polygon:
    """
    Polygon is a sequence of points.
    """

    points: tuple[Coordinate, ...]
    closed: bool = True

    @cached_property
    def bounding_rectangle(self) -> Rectangle:
        """
        Get a rectangle bounding the polygon.

        Returns:
            `Rectangle`: A rectangle bounding the polygon.
        """
        min_x = min(c.left for c in self.points)
        min_y = min(c.top for c in self.points)
        max_x = max(c.left for c in self.points)
        max_y = max(c.top for c in self.points)
        return Rectangle(
            Coordinate(min_x, min_y), Size(max_x - min_x, max_y - min_y)
        )

    @cached_property
    def _mask(self) -> Mask:
        return from_surface(self.fill(Rgba(0, 0, 0, 255)).drawing.pygame)

    def shift(self, coordinate: Coordinate) -> Self:
        return Polygon(
            tuple(c.shift(coordinate) for c in self.points), self.closed
        )

    def fill(self, color: Rgba) -> DrawOnScreen:
        """
        Creates a colored `DrawOnScreen` with the provided color.

        Arguments:
            `Color`: The color to fill the rectangle.

        Returns:
            `DrawOnScreen`: A transparent surface matching rectangle dimensions.
        """
        rect = self.bounding_rectangle
        surf = Surface(rect.size, SRCALPHA)
        negated = [(p.shift(rect.top_left.negate)) for p in self.points]
        polygon(surf, color, negated)
        return DrawOnScreen(rect.top_left, Drawing(surf))

    def collide(self, poly: Self) -> bool:
        """
        Checks if this rectangle overlaps with another polygon.

        Arguments:
            `poly`: The polygon to check for collision with.

        Returns:
            `bool`: True if two polygons overlap, False otherwise.
        """
        if not self.bounding_rectangle.collide(poly.bounding_rectangle):
            return False
        offset = self.bounding_rectangle.top_left.shift(
            poly.bounding_rectangle.top_left.negate
        )
        return bool(self._mask.overlap(poly._mask, offset))

    def contain(self, coordinate: Coordinate) -> bool:
        """
        Checks if a coordinate point lies within this polygon.

        The point is considered inside if it falls in the polygon's bounds,
        including points on the edges.

        Arguments:
            `coordinate`: The coordinate point to check

        Returns:
            `bool`: Whether the coordinate lies within the rectangle.
        """
        x, y = coordinate.shift(self.bounding_rectangle.top_left.negate)
        width, height = self._mask.get_size()
        if 0 <= x < width and 0 <= y < height:
            return bool(self._mask.get_at((x, y)))
        return False


class Rectangle(Polygon):
    """
    A rectangle polygon defined by its top left corner and size.
    """

    def __init__(self, top_left: Coordinate, size: Size) -> None:
        """
        Arguments:
            `top_left`: The top-left corner of the rectangle.

            `size`: The dimensions of the rectangle, including its
                width and height.
        """
        self.top_left = top_left
        self.size = size

    @property
    def left(self) -> Pixel:
        """
        Gets the leftmost x-coordinate of the drawing on the screen.

        Returns:
            `Pixel`: The leftmost x-coordinate.
        """
        return self.top_left.left

    @property
    def right(self) -> Pixel:
        """
        Gets the rightmost x-coordinate of the drawing on the screen.

        Returns:
            `Pixel`: The rightmost x-coordinate (left + width).
        """
        return self.left + self.size.width

    @property
    def top(self) -> Pixel:
        """
        Gets the topmost y-coordinate of the drawing on the screen.

        Returns:
            `Pixel`: The topmost y-coordinate.
        """
        return self.top_left.top

    @cached_property
    def bottom(self) -> Pixel:
        """
        Gets the bottommost y-coordinate of the drawing on the screen.

        Returns:
            `Pixel`: The bottommost y-coordinate (top + height).
        """
        return self.top + self.size.height

    @property
    def top_right(self) -> Coordinate:
        """
        Gets the top-right coordinate of the drawing on the screen.

        Returns:
            `Coordinate`: The top-right coordinate.
        """
        return Coordinate(self.right, self.top)

    @property
    def bottom_left(self) -> Coordinate:
        """
        Gets the bottom-left coordinate of the drawing on the screen.

        Returns:
            `Coordinate`: The bottom-left coordinate.
        """
        return Coordinate(self.left, self.bottom)

    @property
    def bottom_right(self) -> Coordinate:
        """
        Gets the bottom-right coordinate of the drawing on the screen.

        Returns:
            `Coordinate`: The bottom-right coordinate.
        """
        return Coordinate(self.right, self.bottom)

    @property
    def top_center(self) -> Coordinate:
        """
        Gets the center point of the top edge of the drawing on the screen.

        Returns:
            `Coordinate`: The top-center coordinate.
        """
        return Coordinate(self.left + self.size.width / 2, self.top)

    @property
    def bottom_center(self) -> Coordinate:
        """
        Gets the center point of the bottom edge of the drawing on the screen.

        Returns:
            `Coordinate`: The bottom-center coordinate.
        """
        return Coordinate(self.left + self.size.width / 2, self.bottom)

    @property
    def center_left(self) -> Coordinate:
        """
        Gets the center point of the left edge of the drawing on the screen.

        Returns:
            `Coordinate`: The left-center coordinate.
        """
        return Coordinate(self.left, self.top + self.size.height / 2)

    @property
    def center_right(self) -> Coordinate:
        """
        Gets the center point of the right edge of the drawing on the screen.

        Returns:
            `Coordinate`: The right-center coordinate.
        """
        return Coordinate(self.right, self.top + self.size.height / 2)

    @property
    def center(self) -> Coordinate:
        """
        Gets the center point of the drawing on the screen.

        Returns:
            `Coordinate`: The center coordinate of the drawing.
        """
        width, height = self.size
        return Coordinate(self.left + width / 2, self.top + height / 2)

    @property
    def points(self) -> tuple[Coordinate, ...]:
        """
        Get the coordinates of the corners of the rectangle.

        Returns:
            `tuple[Coordinate, ...]`: The coordinates of the corners
                of the rectangle.
        """
        return (
            self.top_left,
            self.top_right,
            self.bottom_right,
            self.bottom_left,
        )

    def collide(self, poly: Polygon) -> bool:
        if isinstance(poly, Rectangle):
            return (
                self.top_left.left < poly.top_right.left
                and self.top_right.left > poly.top_left.left
                and self.top_left.top < poly.bottom_right.top
                and self.bottom_right.top > poly.top_left.top
            )
        return super().collide(poly)

    def contain(self, coordinate: Coordinate) -> bool:
        return (
            self.left < coordinate.left < self.right
            and self.top < coordinate.top < self.bottom
        )

    def shift(self, coordinate: Coordinate) -> Self:
        return Rectangle(self.top_left.shift(coordinate), self.size)
