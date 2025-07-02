"""
Move event.
"""

from collections.abc import Callable
from dataclasses import dataclass

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.scene.scene import Scene


@dataclass
class Move:
    """
    Move event from the current scene to another.

    Attributes:
        `to_object`: Name of the object to move to.

        `trigger_object`: Name of the object to trigger the move.

        `next_scene`: Callable to get the next scene.
    """

    to_object: str
    trigger_object: str
    next_scene: Callable[[CharacterDrawing, str], Scene]

    def to_scene(self, character: CharacterDrawing) -> Scene:
        """
        Move to another scene.

        Arguments:
            `character`: The character to appear in the next scene.

        Returns:
            `Scene`: The next scene.
        """
        return self.next_scene(character, self.to_object)
