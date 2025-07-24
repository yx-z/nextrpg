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
from dataclasses import dataclass
from functools import cached_property
from typing import Self, override

from pygame import SRCALPHA, Mask, Rect, Surface
from pygame.draw import lines, polygon, rect
from pygame.mask import from_surface

from nextrpg.draw.drawing import Drawing
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Pixel, Size
from nextrpg.draw.color import BLACK, Alpha, Rgba
from nextrpg.global_config.global_config import config


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
                area of the drawing on screen.
        """
        coord, size = self.drawing._visible_rectangle
        return Rectangle(self.top_left + coord, size)

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


@dataclass(frozen=True)
class Polygon:
    """
    Represents a polygon shape defined by a sequence of points.

    This class provides polygon functionality including collision detection,
    drawing operations, and geometric calculations. Polygons can be either
    closed (default) or open shapes.

    Arguments:
        `points`: A tuple of coordinates defining the polygon vertices.

        `closed`: Whether the polygon is closed (last point connects to first).
            Defaults to `True`.

    Example:
        ```python
        # Create a triangle
        triangle = Polygon((
            Coordinate(0, 0),
            Coordinate(50, 0),
            Coordinate(25, 50)
        ))

        # Create an open line
        line = Polygon((
            Coordinate(0, 0),
            Coordinate(100, 100)
        ), closed=False)
        ```
    """

    points: tuple[Coordinate, ...]
    closed: bool = True

    @cached_property
    def bounding_rectangle(self) -> Rectangle:
        """
        Get a rectangle bounding the polygon.

        Calculates the smallest rectangle that completely contains
        all points of the polygon.

        Returns:
            `Rectangle`: A rectangle bounding the polygon.

        Example:
            ```python
            polygon = Polygon((Coordinate(0, 0), Coordinate(50, 50)))
            bounds = polygon.bounding_rectangle
            ```
        """
        min_x = min(c.left for c in self.points)
        min_y = min(c.top for c in self.points)
        max_x = max(c.left for c in self.points)
        max_y = max(c.top for c in self.points)
        coord = Coordinate(min_x, min_y)
        size = Size(max_x - min_x, max_y - min_y)
        return Rectangle(coord, size)

    @cached_property
    def _mask(self) -> Mask:
        """
        Get the collision mask for this polygon.

        Creates a pygame mask from the filled polygon for precise
        collision detection.

        Returns:
            `Mask`: The collision mask for this polygon.
        """
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
        poly = lambda surf, points: polygon(surf, color, points)
        return self._draw(poly)

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
        line = lambda surf, points: lines(
            surf, color, self.closed, points, stroke
        )
        return self._draw(line)

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

    def contain(self, coordinate: Coordinate) -> bool:
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

    @cached_property
    def length(self) -> Pixel:
        """
        Get the perimeter length of the polygon.

        Calculates the total length of all edges in the polygon.
        For closed polygons, includes the edge from the last point
        back to the first point.

        Returns:
            `Pixel`: The perimeter length in pixels.

        Example:
            ```python
            triangle = Polygon((Coordinate(0, 0), Coordinate(50, 0),
                              Coordinate(25, 50)))
            perimeter = triangle.length  # Total edge length
            ```
        """
        length = sum(
            p.distance(np) for p, np in zip(self.points, self.points[1:])
        )
        if self.closed:
            length += self.points[0].distance(self.points[-1])
        return length

    def _draw(
        self, surf_and_points: Callable[[Surface, tuple[Coordinate, ...]], None]
    ) -> DrawOnScreen:
        """
        Internal method to create a drawing from the polygon.

        Arguments:
            `surf_and_points`: Function that draws on a surface with points.

        Returns:
            `DrawOnScreen`: The polygon drawing.
        """
        rectangle = self.bounding_rectangle
        surf = Surface(rectangle.size, SRCALPHA)
        negated = tuple(p - rectangle.top_left for p in self.points)
        surf_and_points(surf, negated)
        return DrawOnScreen(rectangle.top_left, Drawing(surf))


class Rectangle(Polygon):
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
    def collide(self, poly: Polygon) -> bool:
        if not isinstance(poly, Rectangle):
            return super().collide(poly)

        return (
            self.top_left.left < poly.top_right.left
            and self.top_right.left > poly.top_left.left
            and self.top_left.top < poly.bottom_right.top
            and self.bottom_right.top > poly.top_left.top
        )

    @override
    def contain(self, coordinate: Coordinate) -> bool:
        return (
            self.left < coordinate.left < self.right
            and self.top < coordinate.top < self.bottom
        )

    def __add__(self, coordinate: Coordinate) -> Self:
        """
        Shift the rectangle by the specified coordinate.

        Arguments:
            `coordinate`: The coordinate to shift the rectangle by.

        Returns:
            `Rectangle`: A new rectangle shifted by the coordinate.
        """
        return Rectangle(self.top_left + coordinate, self.size)

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
        surf = Surface(self.size, SRCALPHA)
        rectangle = Rect(Coordinate(0, 0), self.size)
        rect(surf, color, rectangle, border_radius=border_radius or -1)
        return DrawOnScreen(self.top_left, Drawing(surf))
