from dataclasses import dataclass

from nextrpg.model import export
from nextrpg.core import Direction, Millisecond, PixelPerMillisecond


@export
@dataclass(frozen=True)
class CharacterConfig:
    """
    Configuration class for characters.

    This config is used by `nextrpg.character.character.Character`.

    Attributes:
        `move_speed`: The default speed of the character's movement
            in pixels on screen per physical millisecond.
            The number of pixels is consumed before screen scaling, if any.

        `idle_duration`: The duration of the NPC's idle duration.

        `move_duration`: The duration of the NPC's move duration.

        `directions`: The set of directions that the player can move.
            Default to all directions (up, left, right, down, and diagonals).
    """

    move_speed: PixelPerMillisecond = 0.2
    idle_duration: Millisecond = 500
    move_duration: Millisecond = 1000
    directions: frozenset[Direction] = frozenset(Direction)
