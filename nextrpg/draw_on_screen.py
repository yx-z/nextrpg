"""
Drawable sprites on screen.
"""

from dataclasses import dataclass
from functools import cached_property, lru_cache
from itertools import product
from pathlib import Path
from typing import Final

from pygame import SRCALPHA, Surface, transform
from pygame.image import load

from nextrpg.common_types import Coordinate, Pixel, Rectangle, Size
from nextrpg.config import DebugConfig, config


class Drawing:
    """
    Represents a drawable element and provides methods for accessing its size
    and dimensions.

    This class loads a surface from a file or directly accepts a
    `pygame.Surface` as input.
    It provides properties to access surface dimensions and size and methods to
    crop and scale the surface.
    """

    def __init__(self, resource: Path | Surface) -> None:
        """
        Initializes the object with a resource that is either a file `Path`
        to an image or a `pygame.Surface` object.
        If the resource is a file path, it loads it as a `pygame.Surface`.

        Args:
            `resource`: A `Path` to load a `pygame.Surface` or
                a `pygame.Surface` object to be used directly.
        """
        self._surface: Final[Surface] = (
            load(resource).convert_alpha()
            if isinstance(resource, Path)
            else resource
        )

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
        if debug := config().debug:
            return self._debug_surface(debug)
        return self._surface

    @lru_cache
    def _debug_surface(self, debug: DebugConfig) -> Surface:
        surface = Surface(self.size.tuple, SRCALPHA)
        surface.fill(debug.drawing_background_color.tuple)
        surface.blit(self._surface, Coordinate(0, 0).tuple)
        return surface

    def crop(self, left_top: Coordinate, size: Size) -> "Drawing":
        """
        Crops a rectangular portion of the drawing specified by the
        top-left corner and the size.

        The method extracts a subsection of the drawing based on the provided
        coordinates and dimensions and returns a new `Drawing` instance.
        The original drawing remains unchanged.

        Args:
            `left_top`: The top-left coordinate of the rectangle to be cropped.
            `size`: The width and height of the rectangle to be cropped.

        Returns:
            `Drawing`: A new `Drawing` instance representing the cropped area.
        """
        return Drawing(
            self._surface.subsurface(
                (left_top.left, left_top.top, size.width, size.height)
            )
        )

    def __mul__(self, scale: float) -> "Drawing":
        """
        Scales the drawing surface by a given scale factor.

        This method adjusts the size of the current drawing surface by applying
        a scaling transformation with the specified factor.
        A new `Drawing` instance is returned with the resized surface.

        Args:
            `scale`: The scaling factor to apply to the drawing surface.

        Returns:
            `Drawing`: A new Drawing instance with the scaled surface.
        """
        return Drawing(
            transform.scale(self._surface, (self.size * scale).tuple)
        )


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

    @property
    def pygame(self) -> tuple[Surface, tuple[Pixel, Pixel]]:
        """
        Gets the pygame surface and coordinate tuple for rendering.

        Returns:
            `tuple[pygame.Surface, tuple[float, float]]`:
                A tuple containing the `pygame.Surface` and a tuple of the left
                and top coordinates (x, y).
        """
        return self.drawing.pygame, self.top_left.tuple

    @cached_property
    def visual_bottom(self) -> Pixel:
        width, height = self.drawing.size.tuple
        for h, w in product(reversed(range(int(height))), range(int(width))):
            if not self.drawing.pygame.get_at((w, h)).a:
                return h
        return self.top_left.top

    def __mul__(self, scale: float) -> "DrawOnScreen":
        """
        Scales both the drawing and its position by the given scale factor.

        This method creates a new DrawOnScreen instance with the drawing and
        coordinate both scaled by the provided factor.

        Args:
            `scale`: The scaling factor to apply to both the
                drawing and its position.

        Returns:
            `DrawOnScreen`: New `DrawOnScreen` instance with scaled properties.
        """
        return DrawOnScreen(self.top_left * scale, self.drawing * scale)

    @staticmethod
    def from_rectangle(rectangle: Rectangle) -> "DrawOnScreen":
        """
        Creates a new `DrawOnScreen` instance from a given rectangle.

        Creates a transparent surface with the dimensions of the provided
        rectangle and positions it at the rectangle's top-left coordinate.

        Args:
            `rectangle`: The rectangle that defines the size and position of the
                new `DrawOnScreen` instance.

        Returns:
            `DrawOnScreen`: A transparent surface matching rectangle dimensions.
        """
        return DrawOnScreen(
            rectangle.top_left, Drawing(Surface(rectangle.size.tuple, SRCALPHA))
        )
