"""
Core types referenced across `nextrpg`.
"""

from collections.abc import Callable
from dataclasses import KW_ONLY, dataclass
from enum import Enum, auto
from functools import cached_property
from math import ceil, sqrt
from typing import Any, Union, overload


@dataclass(frozen=True)
class Rgba:
    """
    Represents an RGBA color with red, green, blue and alpha components.

    Arguments:
        `red`: The red component of the color (0-255).

        `green`: The green component of the color (0-255).

        `blue`: The blue component of the color (0-255).

        `alpha`: The alpha (opacity) component of the color (0-255).
    """

    red: int
    green: int
    blue: int
    alpha: int

    @cached_property
    def tuple(self) -> tuple[int, int, int, int]:
        """
        Gets the color components as a tuple.

        Returns:
            `tuple[int, int, int, int]`: A tuple containing the red, green,
            blue and alpha values in that order.
        """
        return self.red, self.green, self.blue, self.alpha


type Millisecond = int
"""
Millisecond elapsed between game loops.
"""

INTERNAL_ONLY: Any = KW_ONLY
"""Used to mark fields as internal-only and not exposed to the library user."""


def init_internal_field(
    self: Any, name: str, factory: Callable[[], Any]
) -> None:
    """
    Used to init `INTERNAL_ONLY` field in `dataclass` instance.

    Args:
        `self`: Object to set.
        `name`: Name of the field.
        `factory`: Factory function to create the value of the field.
            This is a factory to avoid potential side effects when creating
            the field.

    Returns:
        `None`.
    """
    if getattr(self, name) is INTERNAL_ONLY:
        object.__setattr__(self, name, factory())


class Direction(Enum):
    """
    Represents eight directional movements.

    Attributes:

        `DOWN`: Move down and toward the bottom of the screen.

        `LEFT`: Move left and toward the left of the screen.

        `RIGHT`: Move right and toward the right of the screen.

        `UP`: Move up and toward the top of the screen.

        `UP_LEFT`: Move up and left diagonally.

        `UP_RIGHT`: Move up and right diagonally.

        `DOWN_LEFT`: Move down and left diagonally.

        `DOWN_RIGHT`: Move down and right diagonally.
    """

    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    UP_LEFT = auto()
    UP_RIGHT = auto()
    DOWN_LEFT = auto()
    DOWN_RIGHT = auto()


type Pixel = int | float
"""
Number of pixel on screen.

`float` is allowed given Pygame supports passing `float` as `Rect`.
"""


@dataclass(frozen=True)
class DirectionalOffset:
    """
    Represents a directional offset for movement calculations.

    This class combines a direction (one of eight possible directions) with
    an offset value to define movement in 2D space. The vector can be used
    with coordinates to calculate new positions.

    Attributes:
        `direction`: The direction of the vector, defined by `Direction` enum.
            Supports both orthogonal (`UP`, `DOWN`, `LEFT`, `RIGHT`)
            and diagonal (`UP_LEFT`, `UP_RIGHT`, `DOWN_LEFT`, `DOWN_RIGHT`).

        `offset`: The length of movement in pixels.
            This value will be decomposed into x, y pixels upon diagnoal moves.
    """

    direction: Direction
    offset: Pixel


@dataclass(frozen=True)
class Coordinate:
    """
    Represents a 2D coordinate with immutability and provides methods
    for scaling and shifting coordinates.

    Attributes:
        `left`: The horizontal position of the coordinate, measured by
            the number of pixels from the left edge of the game window.

        `top`: The vertical position of the coordinate, measured by
            the number of pixels from the top edge of the game window.
    """

    left: Pixel
    top: Pixel

    def __mul__(self, scale: float) -> "Coordinate":
        """
        Scales the current `Coordinate` values (left and top) by a given factor
        and returns a new `Coordinate` with the scaled values rounded up to the
        nearest integer.

        Round up so that drawings won't leave tiny, black gaps after scaled.

        Args:
            `scale`: The scaling factor to multiply the left and
                top values of the `Coordinate`.

        Returns:
            `Coordinate`: A new `Coordinate` with the scaled and rounded values.
        """
        return Coordinate(ceil(self.left * scale), ceil(self.top * scale))

    @overload
    def __add__(self, offset: DirectionalOffset) -> "Coordinate":
        """
        Shifts the coordinate in the specified direction by a given offset.
        Supports both orthogonal and diagonal directions.

        For diagonal directions, the offset is divided proportionally.
        For example, an offset of `sqrt(2)` in `UP_LEFT` direction shifts
        the coordinate `Pixel(1)` in both `UP` and `LEFT` directions.

        Args:
            `offset`: A `DirectionalOffset` representing the direction
                and offset.

        Returns:
            `Coordinate`: A new coordinate shifted by the specified offset in
            the given direction.
        """

    @overload
    def __add__(self, offset: "Coordinate") -> "Coordinate":
        """
        Add two coordinates together.

        Args:
            `offset`: A `Coordinate`.

        Returns:
            `Coordinate`: A new coordinate shifted by the specified offset.
        """

    def __add__(
        self, offset: Union[DirectionalOffset, "Coordinate"]
    ) -> "Coordinate":
        if isinstance(offset, Coordinate):
            return Coordinate(self.left + offset.left, self.top + offset.top)

        match offset.direction:
            case Direction.UP:
                return Coordinate(self.left, self.top - offset.offset)
            case Direction.DOWN:
                return Coordinate(self.left, self.top + offset.offset)
            case Direction.LEFT:
                return Coordinate(self.left - offset.offset, self.top)
            case Direction.RIGHT:
                return Coordinate(self.left + offset.offset, self.top)

        diag = offset.offset / sqrt(2)
        match offset.direction:
            case Direction.UP_LEFT:
                return Coordinate(self.left - diag, self.top - diag)
            case Direction.UP_RIGHT:
                return Coordinate(self.left + diag, self.top - diag)
            case Direction.DOWN_LEFT:
                return Coordinate(self.left - diag, self.top + diag)
            case Direction.DOWN_RIGHT:
                return Coordinate(self.left + diag, self.top + diag)
            case _:
                raise ValueError(f"Invalid direction: {offset.direction}")

    @cached_property
    def tuple(self) -> tuple[Pixel, Pixel]:
        """
        Gets the coordinates as a tuple.

        Returns:
            `tuple[Pixel, Pixel]`: A tuple containing the left and top
                values in that order.
        """
        return self.left, self.top


@dataclass(frozen=True)
class Size:
    """
    Represents the dimensions of a two-dimensional space, such as an image,
    with defined width and height.

    This class is immutable and designed to encapsulate the concept of size
    in pixel measurements.

    Attributes:
        `width`: The width of the size in pixels.

        `height`: The height of the size in pixels.
    """

    width: Pixel
    height: Pixel

    def __post_init__(self) -> None:
        if self.width < 0 or self.height < 0:
            raise ValueError(
                f"{self.width=} and {self.height=} cannot be negative."
            )

    def __mul__(self, scale: float) -> "Size":
        """
        Scales the dimensions by a scaling factor and returns a new `Size`.

        The new dimensions are rounded up to the nearest integer.

        Round up so that drawings won't leave tiny, black gaps after scaled.

        Args:
            `scale`: A scaling factor by which the width and height will be
                multiplied.

        Returns:
            `Size`: A new `Size` object representing the scaled dimensions.
        """
        return Size(ceil(self.width * scale), ceil(self.height * scale))

    @cached_property
    def tuple(self) -> tuple[Pixel, Pixel]:
        """
        Gets the dimensions as a tuple.

        Returns:
            `tuple[Pixel, Pixel]`: A tuple containing the width and height
                values in that order.
        """
        return self.width, self.height
