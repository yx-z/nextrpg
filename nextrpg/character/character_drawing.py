"""
Character drawing interface.
"""

from abc import ABC, abstractmethod

from nextrpg.common_types import Direction, Millisecond
from nextrpg.draw_on_screen import Drawing


class CharacterDrawing(ABC):
    """
    Interface for drawing characters on screen.
    """

    @property
    @abstractmethod
    def direction(self) -> Direction:
        """
        Get the current direction of the character.

        Returns:
            `Direction`: The current direction of the character.
        """

    @property
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
        Args:
            `direction`: Turn the character facing to this direction.

        Returns:
            `CharacterDrawing`: The updated drawing.
        """

    @abstractmethod
    def move(self, time_delta: Millisecond) -> "CharacterDrawing":
        """
        Returns:
            `CharacterDrawing`:
        """

    @abstractmethod
    def idle(self, time_delta: Millisecond) -> "CharacterDrawing":
        """
        Returns:
            `CharacterDrawing`:
        """
