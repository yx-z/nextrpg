"""
Drawable elements and rendering utilities for `nextrpg`.

This module provides the core drawing system for `nextrpg` games. It defines
classes for representing drawable elements, managing their positioning on
screen, and handling various drawing operations.

Features:
    - `Drawing`: Represents a drawable element with size and surface access
    - `DrawOnScreen`: Combines a drawing with its position on screen
    - `Polygon`: Represents polygon shapes with collision detection
    - `Rectangle`: Specialized rectangle with optimized collision detection
"""

from collections.abc import Callable
from dataclasses import dataclass, replace
from functools import cached_property
from os import PathLike
from typing import Self, override

from pygame import Mask, Rect, SRCALPHA, Surface
from pygame.draw import lines, polygon, rect
from pygame.image import load
from pygame.mask import from_surface

from nextrpg.core.cached_decorator import cached
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Pixel, Size
from nextrpg.core.logger import Logger
from nextrpg.draw.color import Alpha, BLACK, Rgba
from nextrpg.global_config.global_config import config

logger = Logger("Draw")


@cached(
    lambda: config().resource.draw_cache_size,
    lambda resource: None if isinstance(resource, Surface) else resource,
)
@dataclass(frozen=True)
class Draw:
    """
    Represents a drawable element and provides methods for accessing its size
    and dimensions.

    This class loads a surface from a file or directly accepts a
    `pygame.Surface` as input. It provides properties to access surface
    dimensions and size and methods to crop and scale the surface.

    Arguments:
        `resource`: A path to a file containing the drawing resource,
            or a `pygame.Surface` object.

    Example:
        ```python
        # Load from file
        sprite = Drawing("assets/player.png")

        # Use existing surface
        surface = pygame.Surface((32, 32))
        drawing = Drawing(surface)

        # Get dimensions
        size = drawing.size  # Returns Size(width, height)
        width = drawing.width  # Returns int
        ```
    """

    resource: str | PathLike | Surface

    @property
    def width(self) -> Pixel:
        """
        Gets the width of the surface.

        Returns:
            `Pixel`: The width of the surface in pixel measurement.
        """
        return self._surface.width

    @property
    def height(self) -> Pixel:
        """
        Gets the height of the surface.

        Returns:
            `Pixel`: The height of the surface in pixel measurement.
        """
        return self._surface.height

    @property
    def size(self) -> Size:
        """
        Gets the size of an object as a combination of its width and height.

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
            `Draw`: A new `Drawing` instance representing the cropped area.

        Example:
            ```python
            drawing = Drawing("spritesheet.png")
            # Crop a 32x32 sprite from position (64, 0)
            sprite = drawing.crop(Coordinate(64, 0), Size(32, 32))
            ```
        """
        left, top = top_left
        width, height = size
        return Draw(self.pygame.subsurface((left, top, width, height)))

    def set_alpha(self, alpha: Alpha) -> Self:
        """
        Creates a new `Drawing` with the specified alpha value.

        Arguments:
            `alpha`: The new alpha value.

        Returns:
            `Draw`: A new `Drawing` with the specified alpha value.

        Example:
            ```python
            drawing = Drawing("sprite.png")
            transparent = drawing.set_alpha(128)  # 50% transparency
            ```
        """
        surf = self._surface.copy()
        surf.set_alpha(alpha)
        return Draw(surf)

    def draw_on_screen(self, coord: Coordinate) -> DrawOnScreen:
        return DrawOnScreen(coord, self)

    @cached_property
    def _visible_rectangle(self) -> RectangleOnScreen:
        rectangle = self._surface.get_bounding_rect()
        coord = Coordinate(rectangle.x, rectangle.y)
        size = Size(rectangle.width, rectangle.height)
        return RectangleOnScreen(coord, size)

    @cached_property
    def _debug_surface(self) -> Surface | None:
        if not (debug := config().debug) or not (
            color := debug.draw_background_color
        ):
            return None

        surface = Surface(self.size, SRCALPHA)
        surface.fill(color)
        surface.blit(self._surface, (0, 0))
        return surface

    @cached_property
    def _surface(self) -> Surface:
        """
        Get the pygame surface for this drawing.

        Loads the surface from file if needed, or returns the existing
        surface. The surface is converted to alpha format for proper
        transparency support.

        Returns:
            `Surface`: The pygame surface for this drawing.
        """
        if isinstance(self.resource, Surface):
            return self.resource
        logger.debug(t"Loading {self.resource}")
        return load(self.resource).convert_alpha()


@dataclass(frozen=True)
class DrawOnScreen:
    """
    Represents a drawable element positioned on the screen with its coordinates.

    This immutable class combines a drawing with its position and provides
    properties to access various coordinates and dimensions of the drawing
    on the screen.

    Arguments:
        `top_left`: The top-left position of the drawing on the screen.

        `drawing`: The drawable element to be displayed on the screen.

    Example:
        ```python
        sprite = Drawing("player.png")
        player = DrawOnScreen(Coordinate(100, 100), sprite)

        # Get the rectangle bounds
        bounds = player.rectangle

        # Check if point is inside
        is_inside = bounds.contain(Coordinate(120, 120))
        ```
    """

    top_left: Coordinate
    drawing: Draw

    @property
    def rectangle_on_screen(self) -> RectangleOnScreen:
        """
        Gets the rectangular bounds of the drawing on screen.

        Returns:
            `RectangleOnScreen`: A rectangle defining the drawing's position and size
            on screen.
        """
        return RectangleOnScreen(self.top_left, self.drawing.size)

    @cached_property
    def visible_rectangle_on_screen(self) -> RectangleOnScreen:
        """
        Calculate the actual visible bounds of the drawing,
        ignoring transparent pixels.

        Returns:
            `RectangleOnScreen`: A rectangle defining only the visible (non-transparent)
                area of the drawing on screen.
        """
        coord = self.drawing._visible_rectangle.top_left
        size = self.drawing._visible_rectangle.size
        return RectangleOnScreen(self.top_left + coord, size)

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

    def __add__(self, coord: Coordinate) -> Self:
        """
        Shift the drawing by the specified coordinate.

        Arguments:
            `coord`: The coordinate to shift the drawing by.

        Returns:
            `DrawOnScreen`: A new `DrawOnScreen` shifted by the coordinate.
        """
        return DrawOnScreen(self.top_left + coord, self.drawing)

    def __sub__(self, coord: Coordinate) -> Self:
        return self + -coord

    def set_alpha(self, alpha: Alpha) -> Self:
        """
        Set the alpha transparency of the drawing.

        Arguments:
            `alpha`: The alpha value (0-255).

        Returns:
            `DrawOnScreen`: A new `DrawOnScreen` with the specified alpha.

        Example:
            ```python
            player = DrawOnScreen(Coordinate(100, 100), sprite)
            # Make player semi-transparent
            transparent = player.set_alpha(128)
            ```
        """
        return DrawOnScreen(self.top_left, self.drawing.set_alpha(alpha))


class PolygonDraw:
    def __init__(self, points: tuple[Coordinate, ...], color: Rgba) -> None:
        surf = _draw_polygon(points, _fill_polygon(color))
        _set_resource(self, surf)


@dataclass(frozen=True)
class PolygonOnScreen:
    """
    Represents a polygon shape defined by a sequence of points.

    This class provides polygon functionality including collision detection,
    drawing operations, and geometric calculations. Polygons can be either
    closed (default) or open shapes.
    """

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
        return from_surface(self.fill(BLACK).drawing.pygame)

    def fill(self, color: Rgba) -> DrawOnScreen:
        """
        Creates a filled polygon drawing with the provided color.

        Arguments:
            `color`: The color to fill the polygon with.

        Returns:
            `DrawOnScreen`: A drawing of the filled polygon.

        Example:
            ```python
            triangle = Polygon((Coordinate(0, 0), Coordinate(50, 0),
                              Coordinate(25, 50)))
            filled = triangle.fill(Rgba(255, 0, 0, 255))  # Red triangle
            ```
        """
        return self._draw(_fill_polygon(color))

    def line(
        self, color: Rgba, stroke_width: Pixel | None = None
    ) -> DrawOnScreen:
        """
        Creates a line drawing of the polygon with the provided color.

        Arguments:
            `color`: The color of the line.

            `stroke_width`: The width of the line in pixels.
                If `None`, uses the default stroke width from global_config.

        Returns:
            `DrawOnScreen`: A drawing of the polygon outline.

        Example:
            ```python
            triangle = Polygon((Coordinate(0, 0), Coordinate(50, 0),
                              Coordinate(25, 50)))
            outline = triangle.line(Rgba(0, 0, 255, 255), stroke_width=2)
            ```
        """
        if stroke_width is None:
            stroke = config().draw_on_screen.stroke_width
        else:
            stroke = stroke_width

        def _line(surface: Surface, points: tuple[Coordinate, ...]) -> None:
            lines(surface, color, self.closed, points, stroke)

        return self._draw(_line)

    def collide(self, poly: Self) -> bool:
        """
        Checks if this polygon overlaps with another polygon.

        Performs precise collision detection using pygame masks.
        First checks bounding rectangles for efficiency, then
        performs pixel-perfect collision detection.

        Arguments:
            `poly`: The polygon to check for collision with.

        Returns:
            `bool`: `True` if the polygons overlap, `False` otherwise.

        Example:
            ```python
            poly1 = Polygon((Coordinate(0, 0), Coordinate(50, 50)))
            poly2 = Polygon((Coordinate(25, 25), Coordinate(75, 75)))
            is_colliding = poly1.collide(poly2)  # True
            ```
        """
        if not self.bounding_rectangle.collide(poly.bounding_rectangle):
            return False
        offset = (
            self.bounding_rectangle.top_left - poly.bounding_rectangle.top_left
        )
        return bool(self._mask.overlap(poly._mask, offset))

    def __contains__(self, coordinate: Coordinate) -> bool:
        """
        Checks if a coordinate point lies within this polygon.

        The point is considered inside if it falls within the polygon's
        bounds, including points on the edges.

        Arguments:
            `coordinate`: The coordinate point to check.

        Returns:
            `bool`: Whether the coordinate lies within the polygon.

        Example:
            ```python
            triangle = Polygon((Coordinate(0, 0), Coordinate(50, 0),
                              Coordinate(25, 50)))
            is_inside = triangle.contain(Coordinate(25, 25))  # True
            ```
        """
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
        self, size: Size, color: Rgba, border_radius: Pixel | None = None
    ) -> None:
        surface = Surface(size, SRCALPHA)
        rectangle = Rect(Coordinate(0, 0), size)
        rect(surface, color, rectangle, border_radius=border_radius or -1)
        _set_resource(self, surface)


class RectangleOnScreen(PolygonOnScreen):
    """
    A specialized rectangle polygon defined by its top-left corner and size.

    This class provides optimized rectangle operations with efficient
    collision detection and convenient property access for rectangle
    edges and corners.

    Arguments:
        `top_left`: The top-left corner of the rectangle.

        `size`: The dimensions of the rectangle (width and height).

    Example:
        ```python
        # Create a 100x50 rectangle at position (10, 20)
        rect = Rectangle(Coordinate(10, 20), Size(100, 50))

        # Get the center point
        center = rect.center

        # Check if a point is inside
        is_inside = rect.contain(Coordinate(50, 40))
        ```
    """

    def __init__(self, top_left: Coordinate, size: Size) -> None:
        """
        Initialize a rectangle with top-left corner and size.

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
        Gets the leftmost x-coordinate of the rectangle.

        Returns:
            `Pixel`: The leftmost x-coordinate.
        """
        return self.top_left.left

    @property
    def right(self) -> Pixel:
        """
        Gets the rightmost x-coordinate of the rectangle.

        Returns:
            `Pixel`: The rightmost x-coordinate (left + width).
        """
        return self.left + self.size.width

    @property
    def top(self) -> Pixel:
        """
        Gets the topmost y-coordinate of the rectangle.

        Returns:
            `Pixel`: The topmost y-coordinate.
        """
        return self.top_left.top

    @property
    def bottom(self) -> Pixel:
        """
        Gets the bottommost y-coordinate of the rectangle.

        Returns:
            `Pixel`: The bottommost y-coordinate (top + height).
        """
        return self.top + self.size.height

    @property
    def top_right(self) -> Coordinate:
        """
        Gets the top-right coordinate of the rectangle.

        Returns:
            `Coordinate`: The top-right coordinate.
        """
        return Coordinate(self.right, self.top)

    @property
    def bottom_left(self) -> Coordinate:
        """
        Gets the bottom-left coordinate of the rectangle.

        Returns:
            `Coordinate`: The bottom-left coordinate.
        """
        return Coordinate(self.left, self.bottom)

    @property
    def bottom_right(self) -> Coordinate:
        """
        Gets the bottom-right coordinate of the rectangle.

        Returns:
            `Coordinate`: The bottom-right coordinate.
        """
        return Coordinate(self.right, self.bottom)

    @property
    def top_center(self) -> Coordinate:
        """
        Gets the center point of the top edge of the rectangle.

        Returns:
            `Coordinate`: The top-center coordinate.
        """
        return Coordinate(self.left + self.size.width / 2, self.top)

    @property
    def bottom_center(self) -> Coordinate:
        """
        Gets the center point of the bottom edge of the rectangle.

        Returns:
            `Coordinate`: The bottom-center coordinate.
        """
        return Coordinate(self.left + self.size.width / 2, self.bottom)

    @property
    def center_left(self) -> Coordinate:
        """
        Gets the center point of the left edge of the rectangle.

        Returns:
            `Coordinate`: The left-center coordinate.
        """
        return Coordinate(self.left, self.top + self.size.height / 2)

    @property
    def center_right(self) -> Coordinate:
        """
        Gets the center point of the right edge of the rectangle.

        Returns:
            `Coordinate`: The right-center coordinate.
        """
        return Coordinate(self.right, self.top + self.size.height / 2)

    @property
    def center(self) -> Coordinate:
        """
        Gets the center point of the rectangle.

        Returns:
            `Coordinate`: The center coordinate of the rectangle.
        """
        width, height = self.size
        return Coordinate(self.left + width / 2, self.top + height / 2)

    @property
    def points(self) -> tuple[Coordinate, ...]:
        """
        Get the coordinates of the corners of the rectangle.

        Returns the four corner points in clockwise order starting
        from the top-left corner.

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
    def __add__(self, coordinate: Coordinate) -> Self:
        return RectangleOnScreen(self.top_left + coordinate, self.size)

    def fill(
        self, color: Rgba, border_radius: Pixel | None = None
    ) -> DrawOnScreen:
        """
        Creates a filled rectangle drawing with the provided color.

        Arguments:
            `color`: The color to fill the rectangle with.

            `border_radius`: Optional border radius for rounded corners.
                If `None`, creates a rectangle with sharp corners.

        Returns:
            `DrawOnScreen`: A drawing of the filled rectangle.

        Example:
            ```python
            rect = Rectangle(Coordinate(0, 0), Size(100, 50))
            filled = rect.fill(Rgba(255, 0, 0, 255))  # Red rectangle
            rounded = rect.fill(Rgba(0, 255, 0, 255), border_radius=10)
            ```
        """
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


def _set_resource[T](self: T, surface: Surface) -> None:
    object.__setattr__(self, "resource", surface)


def _fill_polygon(
    color: Rgba,
) -> Callable[[Surface, tuple[Coordinate, ...]], None]:
    def fill(surface: Surface, points: tuple[Coordinate, ...]) -> None:
        polygon(surface, color, points)

    return fill
