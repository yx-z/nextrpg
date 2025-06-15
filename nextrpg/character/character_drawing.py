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

    @abstractmethod
    def draw_move(self, direction: Direction) -> Drawing:
        """
        Draw the character's moving visual representation.

        Arguments:
            `direction`: Current facing direction of the character.

        Returns:
            `Drawing`: Contains the character's visual representation.
        """

    @abstractmethod
    def draw_idle(self, direction: Direction) -> Drawing:
        """
        Draw the character's idle visual representation.

        Arguments:
            `direction`: Current facing direction of the character.

        Returns:
            `Drawing`: Contains the character's visual representation.
        """

    @abstractmethod
    def peek_move(
        self, time_delta: Millisecond, direction: Direction
    ) -> Drawing:
        """
        Peek at the character's moving visual representation.

        Arguments:
            `direction`: Current facing direction of the character.

            `time_delta`: Elapsed time since the last  in milliseconds.
        Returns:
            `Drawing`: Contains the character's visual representation.
        """

    @abstractmethod
    def move(
        self, time_delta: Millisecond, direction: Direction
    ) -> "CharacterDrawing":
        """

        Returns:
            `CharacterDrawing`:
        """

    @abstractmethod
    def idle(self, time_delta: Millisecond, direction) -> "CharacterDrawing":
        """
        Returns:
            `CharacterDrawing`:
        """

    @abstractmethod
    def stop(self) -> "CharacterDrawing":
        """

        Returns:
            `CharacterDrawing`:
        """
