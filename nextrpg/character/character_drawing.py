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
    def draw(
        self, time_delta: Millisecond, direction: Direction, is_moving: bool
    ) -> Drawing:
        """
        Draws the character on the screen based on the given parameters.

        Generates the visual representation of the character taking into account
        the time elapsed, facing direction and movement state.

        Arguments:
            `time_delta`: Time has elapsed since the last frame in milliseconds.

            `direction`: Current facing direction of the character.

            `is_moving`: Flag indicating whether the character is in motion.

        Returns:
            `Drawing`: Contains the character's visual representation
        """
