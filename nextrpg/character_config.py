"""
Character configuration system for NextRPG.

This module provides configuration options for character behavior
in NextRPG games. It includes the `CharacterConfig` class which
defines movement, timing, and directional parameters for characters.

The character configuration features:
- Movement speed configuration
- Idle and move duration settings
- Directional movement constraints
- Integration with character systems

Example:
    ```python
    from nextrpg.character_config import CharacterConfig
    from nextrpg.core import Direction, Millisecond, PixelPerMillisecond

    # Create default character config
    config = CharacterConfig()

    # Create custom character config
    custom_config = CharacterConfig(
        move_speed=PixelPerMillisecond(0.5),
        idle_duration=Millisecond(1000),
        directions=frozenset([Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT])
    )
    ```
"""

from dataclasses import dataclass

from nextrpg.core import Direction, Millisecond, PixelPerMillisecond
from nextrpg.model import export


@export
@dataclass(frozen=True)
class CharacterConfig:
    """
    Configuration class for characters.

    This config is used by `nextrpg.character.character.Character`
    to define movement behavior, timing, and directional constraints.

    Arguments:
        `move_speed`: The default speed of the character's movement
            in pixels per millisecond. The number of pixels is consumed
            before screen scaling, if any. Defaults to 0.2.

        `idle_duration`: The duration of the NPC's idle state
            in milliseconds. Defaults to 500ms.

        `move_duration`: The duration of the NPC's move state
            in milliseconds. Defaults to 1000ms.

        `directions`: The set of directions that the character can move.
            Defaults to all directions (up, left, right, down, and diagonals).

    Example:
        ```python
        from nextrpg.character_config import CharacterConfig
        from nextrpg.core import Direction, Millisecond, PixelPerMillisecond

        # Default configuration
        config = CharacterConfig()

        # Fast character
        fast_config = CharacterConfig(
            move_speed=PixelPerMillisecond(0.5),
            idle_duration=Millisecond(200),
            move_duration=Millisecond(500)
        )

        # Orthogonal-only movement
        orthogonal_config = CharacterConfig(
            directions=frozenset([
                Direction.UP, Direction.DOWN,
                Direction.LEFT, Direction.RIGHT
            ])
        )
        ```
    """

    move_speed: PixelPerMillisecond = 0.2
    idle_duration: Millisecond = 500
    move_duration: Millisecond = 1000
    directions: frozenset[Direction] = frozenset(Direction)
