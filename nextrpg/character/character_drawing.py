"""
Character drawing interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import Self

from nextrpg.core import Direction, Millisecond
from nextrpg.draw.draw_on_screen import Drawing


@dataclass(frozen=True)
class CharacterDrawing(ABC):
    """
    Interface for drawing characters on screen.

    Provides abstract methods for rendering character animations and handling
    character movement visualization on the screen.

    Arguments:
        `direction`: Initial character direction.
    """

    direction: Direction

    @cached_property
    @abstractmethod
    def drawing(self) -> Drawing:
        """
        Get the character drawing.

        Returns:
            `nextrpg.draw_on_screen.Drawing`: The character drawing.
        """

    @abstractmethod
    def turn(self, direction: Direction) -> Self:
        """
        Turn the character to face a specified direction.

        Arguments:
            `direction`: Turn the character facing to this direction.

        Returns:
            `CharacterDrawing`: The updated drawing.
        """

    @abstractmethod
    def tick_move(self, time_delta: Millisecond) -> Self:
        """
        Update the character's position based on movement over
        the given time delta.

        Arguments:
            `time_delta`: The amount of time that has passed since the
                last update.

        Returns:
            `CharacterDrawing`: The updated drawing with a new position.
        """

    @abstractmethod
    def tick_idle(self, time_delta: Millisecond) -> Self:
        """
        Update the character's idle animation state over the given time delta.

        Arguments:
            `time_delta`: The amount of time that has passed since the
                last update.

        Returns:
            `CharacterDrawing`: The updated drawing with
                a new idle animation state.
        """
