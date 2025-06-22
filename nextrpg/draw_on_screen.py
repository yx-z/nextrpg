"""
Drawable on screen.
"""

from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from functools import cached_property
from itertools import product
from math import ceil
from pathlib import Path

from pygame import SRCALPHA, Surface
from pygame.image import load

from nextrpg.config import config
from nextrpg.core import (
    Coordinate,
    Pixel,
    Rgba,
    Size,
)
from nextrpg.model import INTERNAL, initialize_internal_field


@dataclass(frozen=True)
class Drawing:
    """
    Represents a drawable element and provides methods for accessing its size
    and dimensions.

    This class loads a surface from a file or directly accepts a
    `pygame.Surface` as input.
    It provides properties to access surface dimensions and size and methods to
    crop and scale the surface.
    """

    resource: Path | Surface
    _: KW_ONLY = INTERNAL
    _surface: Surface = INTERNAL

    @cached_property
    def width(self) -> Pixel:
        """
        Gets the width of the surface.

        Returns:
            `Pixel`: The width of the surface in pixel measurement.
        """
        return self._surface.get_width()

    @cached_property
    def height(self) -> Pixel:
        """
        Gets the height of the surface.

        Returns:
            `Pixel`: The height of the surface in pixel measurement.
        """
        return self._surface.get_height()

    @cached_property
    def size(self) -> Size:
        """
        Gets the size of an object as a combination of its width and height

        Returns:
            `Size`: A Size object containing the width and height of the object.
        """
        return Size(self.width, self.height)

    @cached_property
    def pygame(self) -> Surface:
        """
        Gets the current `pygame.Surface` for the object.

        Returns:
            `pygame.Surface`: The underlying `pygame.Surface`.
        """
        return self._debug_surface or self._surface

    def crop(self, size: Size, left_top: Coordinate) -> Drawing:
        """
        Crops a rectangular portion of the drawing specified by the
        top-left corner and the size.

        The method extracts a subsection of the drawing based on the provided
        coordinates and dimensions and returns a new `Drawing` instance.
        The original drawing remains unchanged.

        Args:
            `size`: The width and height of the rectangle to be cropped.

            `left_top`: The top-left coordinate of the rectangle to be cropped.

        Returns:
            `Drawing`: A new `Drawing` instance representing the cropped area.
        """
        return Drawing(
            self._surface.subsurface(
                (left_top.left, left_top.top, size.width, size.height)
            )
        )

    @cached_property
    def _debug_surface(self) -> Surface | None:
        if not (debug := config().debug):
            return None
        surface = Surface(self.size.tuple, SRCALPHA)
        surface.fill(debug.drawing_background_color.tuple)
        surface.blit(self._surface, (0, 0))
        return surface

    def __post_init__(self) -> None:
        initialize_internal_field(
            self,
            "_surface",
            lambda: (
                load(self.resource).convert_alpha()
                if isinstance(self.resource, Path)
                else self.resource
            ),
        )


@dataclass(frozen=True)
class Rectangle:
    """
    Represents an immutable rectangle defined by its top left corner and size.

    Attributes:
        `top_left`: The top-left corner of the rectangle.

        `size`: The dimensions of the rectangle, including its width and height.
    """

    top_left: Coordinate
    size: Size

    @cached_property
    def left(self) -> Pixel:
        """
        Gets the leftmost x-coordinate of the drawing on the screen.

        Returns:
            `Pixel`: The leftmost x-coordinate.
        """
        return self.top_left.left

    @cached_property
    def right(self) -> Pixel:
        """
        Gets the rightmost x-coordinate of the drawing on the screen.

        Returns:
            `Pixel`: The rightmost x-coordinate (left + width).
        """
        return self.left + self.size.width

    @cached_property
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

    @cached_property
    def top_right(self) -> Coordinate:
        """
        Gets the top-right coordinate of the drawing on the screen.

        Returns:
            `Coordinate`: The top-right coordinate.
        """
        return Coordinate(self.right, self.top)

    @cached_property
    def bottom_left(self) -> Coordinate:
        """
        Gets the bottom-left coordinate of the drawing on the screen.

        Returns:
            `Coordinate`: The bottom-left coordinate.
        """
        return Coordinate(self.left, self.bottom)

    @cached_property
    def bottom_right(self) -> Coordinate:
        """
        Gets the bottom-right coordinate of the drawing on the screen.

        Returns:
            `Coordinate`: The bottom-right coordinate.
        """
        return Coordinate(self.right, self.bottom)

    @cached_property
    def top_center(self) -> Coordinate:
        """
        Gets the center point of the top edge of the drawing on the screen.

        Returns:
            `Coordinate`: The top-center coordinate.
        """
        return Coordinate(self.left + self.size.width / 2, self.top)

    @cached_property
    def bottom_center(self) -> Coordinate:
        """
        Gets the center point of the bottom edge of the drawing on the screen.

        Returns:
            `Coordinate`: The bottom-center coordinate.
        """
        return Coordinate(self.left + self.size.width / 2, self.bottom)

    @cached_property
    def center_left(self) -> Coordinate:
        """
        Gets the center point of the left edge of the drawing on the screen.

        Returns:
            `Coordinate`: The left-center coordinate.
        """
        return Coordinate(self.left, self.top + self.size.height / 2)

    @cached_property
    def center_right(self) -> Coordinate:
        """
        Gets the center point of the right edge of the drawing on the screen.

        Returns:
            `Coordinate`: The right-center coordinate.
        """
        return Coordinate(self.right, self.top + self.size.height / 2)

    @cached_property
    def center(self) -> Coordinate:
        """
        Gets the center point of the drawing on the screen.

        Returns:
            `Coordinate`: The center coordinate of the drawing.
        """
        return Coordinate(
            self.left + self.size.width / 2, self.top + self.size.height / 2
        )

    def collide(self, rectangle: Rectangle) -> bool:
        """
        Checks if this rectangle overlaps with another rectangle.

        This method determines if there is any overlap between the
        current rectangle and the provided rectangle by
        comparing their edge coordinates.

        Args:
            `rectangle`: The rectangle to check for collision with.

        Returns:
            `bool`: True if the rectangles overlap, False otherwise.
        """
        return (
            self.top_left.left < rectangle.top_right.left
            and self.top_right.left > rectangle.top_left.left
            and self.top_left.top < rectangle.bottom_right.top
            and self.bottom_right.top > rectangle.top_left.top
        )

    def __contains__(self, coordinate: Coordinate) -> bool:
        """
        Checks if a coordinate point lies within this rectangle.

        The point is considered inside if it falls in the rectangle's bounds,
        including points on the edges.

        Arguments:
            `coordinate`: The coordinate point to check

        Returns:
            `bool`: Whether the coordinate lies within the rectangle.
        """
        return (
            self.left < coordinate.left < self.right
            and self.top < coordinate.top < self.bottom
        )

    def fill(self, color: Rgba) -> DrawOnScreen:
        """
        Creates a colored `DrawOnScreen` with the provided color.

        Args:
            `Color`: The color to fill the rectangle.

        Returns:
            `DrawOnScreen`: A transparent surface matching rectangle dimensions.
        """
        surface = Surface(self.size.tuple, SRCALPHA)
        surface.fill(color.tuple)
        return DrawOnScreen(self.top_left, Drawing(surface))


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

    @cached_property
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
        visible = [
            Coordinate(x, y)
            for x, y in product(
                range(ceil(self.drawing.width)),
                range(ceil(self.drawing.height)),
            )
            # `drawing._surface` to ignore the debug background.
            if self.drawing._surface.get_at((x, y)).a
        ]
        if not visible:
            return Rectangle(Coordinate(0, 0), Size(0, 0))

        min_x = min(visible, key=lambda c: c.left).left
        min_y = min(visible, key=lambda c: c.top).top
        max_x = max(visible, key=lambda c: c.left).left
        max_y = max(visible, key=lambda c: c.top).top
        return Rectangle(
            self.top_left + Coordinate(min_x, min_y),
            Size(max_x - min_x, max_y - min_y),
        )

    @cached_property
    def pygame(self) -> tuple[Surface, tuple[Pixel, Pixel]]:
        """
        Gets the pygame surface and coordinate tuple for rendering.

        Returns:
            `tuple[pygame.Surface, tuple[float, float]]`:
                A tuple containing the `pygame.Surface` and a tuple of the left
                and top coordinates (x, y).
        """
        return self.drawing.pygame, self.top_left.tuple

    def __add__(self, coord: Coordinate) -> DrawOnScreen:
        """
        Shift the drawing by the specified coordinate.

        Args:
            `coord`: The coordinate to shift the drawing by.

        Returns:
            `DrawOnScreen`: A new `DrawOnScreen` shifted by the coordinate.
        """
        return DrawOnScreen(self.top_left + coord, self.drawing)
