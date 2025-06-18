"""
Character drawing interface.
"""

from abc import ABC, abstractmethod
from functools import cached_property

from nextrpg.core import Direction, Millisecond
from nextrpg.draw_on_screen import Drawing


class CharacterDrawing(ABC):
    """
    Interface for drawing characters on screen.

    Provides abstract methods for rendering character animations and handling
    character movement visualization on the screen.
    """

    @cached_property
    @abstractmethod
    def direction(self) -> Direction:
        """
        Get the current direction of the character.

        Returns:
            `Direction`: The current direction of the character.
        """

    @cached_property
    @abstractmethod
    def drawing(self) -> Drawing:
        """
        Draw the character's moving visual representation.

        Returns:
            `Drawing`: Contains the character's visual representation.
        """

    @abstractmethod
    def turn(self, direction: Direction) -> "CharacterDrawing":
        """
        Turn the character to face a specified direction.

        Args:
            `direction`: Turn the character facing to this direction.

        Returns:
            `CharacterDrawing`: The updated drawing.
        """

    @abstractmethod
    def move(self, time_delta: Millisecond) -> "CharacterDrawing":
        """
        Update the character's position based on movement over
        the given time delta.

        Args:
            `time_delta`: The amount of time that has passed since the
                last update.

        Returns:
            `CharacterDrawing`: The updated drawing with a new position.
        """

    @abstractmethod
    def idle(self, time_delta: Millisecond) -> "CharacterDrawing":
        """
        Update the character's idle animation state over the given time delta.

        Args:
            `time_delta`: The amount of time that has passed since the
                last update.

        Returns:
            `CharacterDrawing`: The updated drawing with
                a new idle animation state.
        """
