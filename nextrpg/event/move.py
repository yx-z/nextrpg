"""
Move event.
"""

from collections.abc import Callable
from dataclasses import dataclass

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_on_screen import CharacterSpec
from nextrpg.scene.scene import Scene
from nextrpg.scene.static_scene import StaticScene
from nextrpg.scene.transition_triple import TransitionTriple


@dataclass(frozen=True)
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
    next_scene: Callable[[CharacterSpec], Scene]

    def to_scene(
        self, from_scene: Scene, character: CharacterDrawing
    ) -> TransitionTriple:
        """
        Move to another scene.

        Arguments:
            `from_scene`: The current scene.

            `character`: The character to appear in the next scene.

        Returns:
            `TransitionScene`: The transition to the next scene.
        """
        return TransitionTriple(
            from_scene=from_scene,
            intermediary=StaticScene(),
            to_scene=self.next_scene(
                CharacterSpec(name=self.to_object, character=character)
            ),
        )
