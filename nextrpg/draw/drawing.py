from dataclasses import dataclass
from functools import cached_property
from os import PathLike
from typing import NamedTuple, Self

from pygame import SRCALPHA, Surface
from pygame.image import load

from nextrpg.core.logger import Logger
from nextrpg.draw.color import Alpha
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Pixel, Size
from nextrpg.global_config.global_config import config
from nextrpg.core.cached_decorator import cached

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
            `Drawing`: A new `Drawing` instance representing the cropped area.

        Example:
            ```python
            drawing = Drawing("spritesheet.png")
            # Crop a 32x32 sprite from position (64, 0)
            sprite = drawing.crop(Coordinate(64, 0), Size(32, 32))
            ```
        """
        left, top = top_left
        width, height = size
        return Drawing(self.pygame.subsurface((left, top, width, height)))

    def set_alpha(self, alpha: Alpha) -> Self:
        """
        Creates a new `Drawing` with the specified alpha value.

        Arguments:
            `alpha`: The new alpha value.

        Returns:
            `Drawing`: A new `Drawing` with the specified alpha value.

        Example:
            ```python
            drawing = Drawing("sprite.png")
            transparent = drawing.set_alpha(128)  # 50% transparency
            ```
        """
        surf = self._surface.copy()
        surf.set_alpha(alpha)
        return Drawing(surf)

    @cached_property
    def _visible_rectangle(self) -> _Rectangle:
        rectangle = self._surface.get_bounding_rect()
        coord = Coordinate(rectangle.x, rectangle.y)
        size = Size(rectangle.width, rectangle.height)
        return _Rectangle(coord, size)

    @cached_property
    def _debug_surface(self) -> Surface | None:
        if not (debug := config().debug) or not (
            color := debug.drawing_background_color
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


class _Rectangle(NamedTuple):
    coord: Coordinate
    size: Size
