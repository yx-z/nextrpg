"""
Common types referenced across `nextrpg`.
"""

from dataclasses import dataclass
from enum import Enum, auto
from math import ceil, sqrt
from typing import Union, overload


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

    @property
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

        Round up so that sprites won't leave tiny, unrendered gaps after scaled.

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
            `offset`: A `DirectionalOffset` representing the direction and offset.

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

    @property
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

    def __mul__(self, scale: float) -> "Size":
        """
        Scales the dimensions by a scaling factor and returns a new `Size`.

        The new dimensions are rounded up to the nearest integer.

        Round up so that sprites won't leave tiny, unrendered gaps after scaled.

        Args:
            `scale`: A scaling factor by which the width and height will be
                multiplied.

        Returns:
            `Size`: A new `Size` object representing the scaled dimensions.
        """
        return Size(ceil(self.width * scale), ceil(self.height * scale))

    @property
    def tuple(self) -> tuple[Pixel, Pixel]:
        """
        Gets the dimensions as a tuple.

        Returns:
            `tuple[Pixel, Pixel]`: A tuple containing the width and height
                values in that order.
        """
        return self.width, self.height


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

    @property
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
        return Coordinate(
            self.left + self.size.width / 2, self.top + self.size.height / 2
        )

    def collides(self, rectangle: "Rectangle") -> bool:
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
            self.top_left.left <= rectangle.top_right.left
            and self.top_right.left >= rectangle.top_left.left
            and self.top_left.top <= rectangle.bottom_right.top
            and self.bottom_right.top >= rectangle.top_left.top
        )

    def __mul__(self, scale: float) -> "Rectangle":
        """
        Scales both the position and size of the rectangle by the scale factor.

        This method creates a new `Rectangle` instance with both the top-left
        coordinate and size scaled by the provided factor.

        Args:
            `scale`: The scaling factor to apply to both position and size.

        Returns:
            `Rectangle`: A new `Rectangle` instance with scaled properties.
        """
        return Rectangle(self.top_left * scale, self.size * scale)

    def __add__(self, vector: DirectionalOffset) -> "Rectangle":
        """Shifts the rectangle in the specified direction by a given offset.
        Supports both orthogonal and diagonal directions.

        For diagonal directions, the offset is divided proportionally.

        For example, an offset of `sqrt(2)` in `UP_LEFT` direction shifts
        the coordinate `Pixel(1)` in both `UP` and `LEFT` directions.

        Args:
            `vector`: A `PolarVector` object representing the direction and offset.

        Returns:
            `Rectangle`: A new rectangle shifted by the specified vector.
        """
        return Rectangle(self.top_left + vector, self.size)

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
            self.left <= coordinate.left <= self.right
            and self.top <= coordinate.top <= self.bottom
        )
