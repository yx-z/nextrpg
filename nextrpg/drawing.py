from dataclasses import dataclass
from functools import cached_property
from os import PathLike
from typing import Self

from pygame import SRCALPHA, Surface
from pygame.image import load

from nextrpg.config import config
from nextrpg.coordinate import Coordinate
from nextrpg.core import Alpha, Pixel, Size
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
