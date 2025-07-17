"""
Character configuration system for `nextrpg`.

This module provides configuration options for character behavior in
`nextrpg` games. It includes the `CharacterConfig` class which defines
movement, timing, and directional parameters for characters.

Features:
    - Movement speed configuration
    - Idle and move duration settings
    - Directional movement constraints
    - Integration with character systems
"""

from dataclasses import dataclass

from nextrpg.core.dimension import PixelPerMillisecond
from nextrpg.core.direction import Direction
from nextrpg.core.time import Millisecond


@dataclass(frozen=True)
class CharacterConfig:
    """
    Configuration class for characters.

    This global_config is used by `nextrpg.character.character.Character` to define
    movement behavior, timing, and directional constraints.

    Arguments:
        move_speed: The default speed of the character's movement in pixels
            per millisecond. The number of pixels is consumed before screen
            scaling, if any. Defaults to 0.2.
        idle_duration: The duration of the NPC's idle state in milliseconds.
            Defaults to 500.
        move_duration: The duration of the NPC's move state in milliseconds.
            Defaults to 1000.
        directions: The set of directions that the character can move.
            Defaults to all directions (up, left, right, down, and diagonals).
    """

    move_speed: PixelPerMillisecond = 0.2
    idle_duration: Millisecond = 500
    move_duration: Millisecond = 1000
    directions: frozenset[Direction] = frozenset(Direction)
