from dataclasses import dataclass
from enum import Enum, auto
from typing import Self

from nextrpg.core.dimension import Pixel


class Direction(Enum):
    """
    Represents eight directional movements for character and object positioning.

    This enum provides all possible directions for movement in a 2D grid,
    including both orthogonal (up, down, left, right) and diagonal
    movements. Each direction represents a unit vector in 2D space.

    Attributes:
        `DOWN`: Move down and toward the bottom of the screen.

        `LEFT`: Move left and toward the left of the screen.

        `RIGHT`: Move right and toward the right of the screen.

        `UP`: Move up and toward the top of the screen.

        `UP_LEFT`: Move up and left diagonally.

        `UP_RIGHT`: Move up and right diagonally.

        `DOWN_LEFT`: Move down and left diagonally.

        `DOWN_RIGHT`: Move down and right diagonally.

    Example:
        ```python
        # Get the opposite direction
        opposite = Direction.UP.opposite  # Returns Direction.DOWN

        # Check if direction is diagonal
        is_diagonal = direction in [Direction.UP_LEFT, Direction.UP_RIGHT,
                                   Direction.DOWN_LEFT, Direction.DOWN_RIGHT]
        ```
    """

    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    UP_LEFT = auto()
    UP_RIGHT = auto()
    DOWN_LEFT = auto()
    DOWN_RIGHT = auto()

    @property
    def opposite(self) -> Self:
        """
        Get the opposite direction.

        Returns:
            `Direction`: The direction opposite to the current direction.
        """
        return _OPPOSITE_DIRECTION[self]


_OPPOSITE_DIRECTION = {
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
    Direction.UP: Direction.DOWN,
    Direction.UP_LEFT: Direction.DOWN_RIGHT,
    Direction.UP_RIGHT: Direction.DOWN_LEFT,
    Direction.DOWN_LEFT: Direction.UP_RIGHT,
    Direction.DOWN_RIGHT: Direction.UP_LEFT,
}


@dataclass(frozen=True)
class DirectionalOffset:
    """
    Represents a directional offset for movement calculations.

    This class combines a direction (one of eight possible directions) with
    an offset value to define movement in 2D space. The vector can be used
    with coordinates to calculate new positions.

    Arguments:
        `direction`: The direction of the vector, defined by `Direction` enum.
            Supports both orthogonal (`UP`, `DOWN`, `LEFT`, `RIGHT`)
            and diagonal (`UP_LEFT`, `UP_RIGHT`, `DOWN_LEFT`, `DOWN_RIGHT`).

        `offset`: The length of movement in pixels.
            This value will be decomposed into x, y pixels upon diagonal moves.

    Example:
        ```python
        # Create a movement offset of 5 pixels upward
        movement = DirectionalOffset(Direction.UP, 5)

        # Create a diagonal movement
        diagonal = DirectionalOffset(Direction.UP_RIGHT, 10)
        ```
    """

    direction: Direction
    offset: Pixel
