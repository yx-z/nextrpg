"""
Core types and utilities used throughout the NextRPG framework.

This module provides fundamental data structures and utilities that are
referenced across the entire NextRPG framework. It includes:

- Color representation (`Rgba`)
- Directional movement (`Direction`, `DirectionalOffset`)
- Size and dimension handling (`Size`)
- Font management (`Font`)
- Timer utilities (`Timer`)
- Type aliases for common concepts

These types form the foundation for character movement, drawing,
and game mechanics throughout the framework.

Example:
    ```python
    from nextrpg.core import Direction, Size, Rgba

    # Create a size for a sprite
    sprite_size = Size(32, 32)

    # Define a color
    red_color = Rgba(255, 0, 0, 255)

    # Use directions for movement
    movement = Direction.UP
    ```
"""

from collections import namedtuple
from dataclasses import dataclass, replace
from enum import Enum, auto
from functools import cached_property
from math import ceil
from typing import Self

import pygame
from pygame.font import SysFont
from pygame.time import get_ticks

from nextrpg.model import export


type Alpha = int
"""
Alpha channel that defines the transparency between [0, 255] for images.
0 is fully transparent, 255 is fully opaque.
"""


@export
def alpha_from_percentage(percentage: float) -> Alpha:
    """
    Convert a percentage value to an alpha channel value.

    Converts a percentage (0.0 to 1.0) to an alpha channel value
    (0 to 255) for transparency calculations.

    Arguments:
        `percentage`: A float between 0.0 and 1.0 representing
            the transparency percentage.

    Returns:
        `Alpha`: An integer between 0 and 255 representing the
            alpha channel value.

    Example:
        ```python
        alpha = alpha_from_percentage(0.5)  # Returns 127
        ```
    """
    return int(255 * percentage)


@export
class Rgba(namedtuple("Rgba", "red green blue alpha")):
    """
    Represents an RGBA color with red, green, blue and alpha components.

    This immutable class provides a convenient way to represent colors
    with transparency support. All components are integers in the range
    0-255, where 0 represents no intensity and 255 represents full
    intensity.

    Arguments:
        `red`: The red component of the color (0-255).

        `green`: The green component of the color (0-255).

        `blue`: The blue component of the color (0-255).

        `alpha`: The alpha (opacity) component of the color (0-255).
            0 is fully transparent, 255 is fully opaque.

    Example:
        ```python
        # Create a semi-transparent red color
        red_color = Rgba(255, 0, 0, 128)

        # Create a fully opaque white color
        white_color = Rgba(255, 255, 255, 255)
        ```
    """

    red: int
    green: int
    blue: int
    alpha: Alpha


BLACK = Rgba(0, 0, 0, 255)
WHITE = Rgba(255, 255, 255, 255)

type Millisecond = int | float
"""
Millisecond elapsed between game loops.
"""


@export
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
    def opposite(self) -> Direction:
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

type Pixel = int | float
"""
Number of pixel on screen.

`float` is allowed given Pygame supports passing `float` as `Rect`.
"""

type PixelPerMillisecond = int | float
"""
Used as a unit for speed.
"""


@export
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


@export
class Size(namedtuple("Size", "width height")):
    """
    Represents the dimensions of a two-dimensional space.

    This class is immutable and designed to encapsulate the concept of size
    in pixel measurements. It provides utility methods for scaling and
    manipulation of dimensions.

    Arguments:
        `width`: The width of the size in pixels.

        `height`: The height of the size in pixels.

    Example:
        ```python
        # Create a size for a sprite
        sprite_size = Size(32, 32)

        # Scale the size
        scaled_size = sprite_size.scale(2.0)  # Returns Size(64, 64)
        ```
    """

    width: Pixel
    height: Pixel

    def scale(self, scaling: float) -> Self:
        """
        Scales the dimensions by a scaling factor and returns a new `Size`.

        The new dimensions are rounded up to the nearest integer to ensure
        that drawings won't leave tiny, black gaps after scaling.

        Arguments:
            `scaling`: A scaling factor by which the width and height will be
                multiplied.

        Returns:
            `Size`: A new `Size` object representing the scaled dimensions.

        Example:
            ```python
            size = Size(10, 20)
            scaled = size.scale(1.5)  # Returns Size(15, 30)
            ```
        """
        return Size(ceil(self.width * scaling), ceil(self.height * scaling))

    def __repr__(self) -> str:
        return f"({self.width}, {self.height})"


@export
@dataclass(frozen=True)
class Font:
    """
    Font configuration for text rendering in the game.

    This class provides a convenient way to configure fonts for text
    rendering. It supports both system fonts and custom font files,
    with automatic pygame font object creation.

    Arguments:
        `size`: Font size in pixels.

        `name`: Font name. If `None`, uses the default system font.

    Example:
        ```python
        # Create a font with default system font
        font = Font(16)

        # Create a font with specific name
        custom_font = Font(24, "Arial")

        # Get text dimensions
        text_size = font.text_size("Hello World")
        ```
    """

    size: int
    name: str | None = None

    @cached_property
    def pygame(self) -> pygame.Font:
        """
        Get the pygame font object.

        Creates and caches a pygame Font object based on the font
        configuration. This is used internally for text rendering.

        Returns:
            `pygame.Font`: Pygame font object for text rendering.
        """
        return SysFont(self.name, self.size)

    def text_size(self, text: str) -> Size:
        """
        Get the drawing size of a text string.

        Calculates the pixel dimensions required to render the given
        text string with this font configuration.

        Arguments:
            `text`: The text string to measure.

        Returns:
            `Size`: The size of the text string in pixels.

        Example:
            ```python
            font = Font(16)
            size = font.text_size("Hello")  # Returns Size(width, height)
            ```
        """
        width, height = self.pygame.size(text)
        return Size(width, height)

    @cached_property
    def text_height(self) -> Pixel:
        """
        Get the line height of the font.

        Returns:
            `Pixel`: The line height in pixels.
        """
        return self.pygame.get_linesize()


@export
@dataclass(frozen=True)
class Timer:
    """
    A timer with duration and elapsed time tracking.

    This class provides a simple timer mechanism for tracking elapsed
    time and determining when a timer has completed. It's commonly
    used for animations, delays, and time-based game mechanics.

    Arguments:
        `duration`: The total duration of the timer in milliseconds.

        `elapsed`: The elapsed time in milliseconds. Defaults to 0.

    Example:
        ```python
        # Create a 2-second timer
        timer = Timer(2000)

        # Update timer in game loop
        timer = timer.tick(time_delta)

        # Check if timer is complete
        if timer.complete:
            print("Timer finished!")
        ```
    """

    duration: Millisecond
    elapsed: Millisecond = 0

    def tick(self, time_delta: Millisecond) -> Self:
        """
        Tick the timer in a game loop.

        Advances the timer by the given time delta and returns a new
        timer instance with updated elapsed time.

        Arguments:
            `time_delta`: The time elapsed since the last tick in
                milliseconds.

        Returns:
            `Timer`: A new timer with elapsed time updated.

        Example:
            ```python
            timer = Timer(1000)  # 1 second timer
            timer = timer.tick(100)  # Advance by 100ms
            ```
        """
        return replace(self, elapsed=self.elapsed + time_delta)

    @cached_property
    def reset(self) -> Self:
        """
        Get a reset timer.

        Creates a new timer instance with the same duration but
        elapsed time set to 0.

        Returns:
            `Timer`: A new timer with elapsed time set to 0.

        Example:
            ```python
            timer = Timer(1000, 500)  # 1s timer, 500ms elapsed
            reset_timer = timer.reset  # 1s timer, 0ms elapsed
            ```
        """
        return replace(self, elapsed=0)

    @cached_property
    def complete(self) -> bool:
        """
        Get whether the timer has completed.

        Returns:
            `bool`: Whether the timer has completed (elapsed >= duration).

        Example:
            ```python
            timer = Timer(1000, 1200)  # 1s timer, 1.2s elapsed
            if timer.complete:
                print("Timer is done!")
            ```
        """
        return self.elapsed > self.duration


type Timepoint = int | float


@export
def get_timepoint() -> Timepoint:
    """
    Get the current time point in milliseconds.

    Returns the current time from pygame's clock, which is typically
    used for calculating time deltas in game loops.

    Returns:
        `Timepoint`: Current time in milliseconds.

    Example:
        ```python
        start_time = get_timepoint()
        # ... do some work ...
        end_time = get_timepoint()
        elapsed = end_time - start_time
        ```
    """
    return get_ticks()
