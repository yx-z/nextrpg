from collections.abc import Callable

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.model import Model
from nextrpg.scene.scene import Scene


class Move(Model):
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

        Args:
            `character`: The character to appear on the next scene.

        Returns:
            `Scene`: The next scene.
        """
        return self.next_scene(character, self.to_object)
