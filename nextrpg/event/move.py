from collections.abc import Callable

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.model import Model
from nextrpg.scene.scene import Scene


class Move(Model):
    trigger_object: str
    to_object: str
    to_map: Callable[[CharacterDrawing, str], Scene]
