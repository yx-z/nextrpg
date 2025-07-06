"""
Core types referenced across `nextrpg`.
"""

from collections import namedtuple
from dataclasses import dataclass, replace
from enum import Enum, auto
from functools import cached_property
from math import ceil
from typing import Self

import pygame
from pygame.font import SysFont

type Alpha = int
"""
Alpha channel that defines the transparency between [0, 255] for images.
0 is fully transparent, 255 is fully opaque.
"""


class Rgba(namedtuple("Rgba", "red green blue alpha")):
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
    alpha: Alpha


type Millisecond = int | float
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

    @property
    def opposite(self) -> Direction:
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

type Pixel = int | float
"""
Number of pixel on screen.

`float` is allowed given Pygame supports passing `float` as `Rect`.
"""

type PixelPerMillisecond = int | float
"""
Used as a unit for speed.
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


class Size(namedtuple("Size", "width height")):
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

    def scale(self, scaling: float) -> Self:
        """
        Scales the dimensions by a scaling factor and returns a new `Size`.

        The new dimensions are rounded up to the nearest integer.

        Round up so that drawings won't leave tiny, black gaps after scaled.

        Arguments:
            `scaling`: A scaling factor by which the width and height will be
                multiplied.

        Returns:
            `Size`: A new `Size` object representing the scaled dimensions.
        """
        return Size(ceil(self.width * scaling), ceil(self.height * scaling))

    def __repr__(self) -> str:
        return f"({self.width}, {self.height})"


@dataclass(frozen=True)
class Font:
    """
    Font for text in game.

    Arguments:
        `size`: Font size in pixels.

        `name`: Font name. If `None`, uses the default system font.
    """

    size: int
    name: str | None = None

    @cached_property
    def pygame(self) -> pygame.Font:
        """
        Get the pygame font object.

        Returns:
            `pygame.Font`: Pygame font object.
        """
        return SysFont(self.name, self.size)

    def text_size(self, text: str) -> Size:
        """
        Get the drawing size of a text string.

        Arguments:
            `text`: The text string to measure.

        Returns:
            `Size`: The size of the text string.
        """
        width, height = self.pygame.size(text)
        return Size(width, height)


@dataclass(frozen=True)
class Timer:
    """
    A timer with duration and elapsed time.
    """

    duration: Millisecond
    elapsed: Millisecond = 0

    def tick(self, time_delta: Millisecond) -> Self:
        """
        Tick the timer in a game loop.

        Arguments:
            `time_delta`: The time elapsed since the last tick.

        Returns:
            `Timer`: A new timer with elapsed time updated.
        """
        return replace(self, elapsed=self.elapsed + time_delta)

    @cached_property
    def reset(self) -> Self:
        """
        Get a reset timer.

        Returns:
            `Timer`: A new timer with elapsed time set to 0.
        """
        return replace(self, elapsed=0)

    @cached_property
    def expired(self) -> bool:
        """
        Get whether the timer has expired.

        Returns:
            `bool`: Whether the timer has expired.
        """
        return self.elapsed > self.duration
