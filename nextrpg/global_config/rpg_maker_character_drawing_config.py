"""
RPG Maker character drawing configuration system for `NextRPG`.

This module provides configuration options for RPG Maker character sprites in
`NextRPG` games. It includes the `RpgMakerCharacterDrawingConfig` class which
defines animation timing and behavior for character sprites.

The RPG Maker character drawing configuration features:
- Frame duration configuration
- Animation timing control
- RPG Maker sprite sheet compatibility
- Character animation behavior

Note: `NextRPG` is only compatible with the RPG Maker character sprite sheet
format to be able to re-use existing resources. However, using RPG Maker's
Runtime Time Package (RTP) in non-RPG Maker frameworks violates the license of
RPG Maker, even if you own a copy of RPG Maker.
"""

from dataclasses import dataclass

from nextrpg.core.time import Millisecond


@dataclass(frozen=True)
class RpgMakerCharacterDrawingConfig:
    """
    Configuration class for RPG Maker character drawings.

    This global_config is used by `nextrpg.character.rpg_maker_drawing.RpgMakerCharacterDrawing`
    to control how character sprites are animated and displayed. It defines the
    animation timing, idle behavior, and default orientation.

    Note that `nextrpg` is only compatible with the RPG Maker character sprite
    sheet format to be able to re-use existing resources. However, using RPG
    Maker's Runtime Time Package (RTP) in non-RPG Maker frameworks violates the
    license of RPG Maker, even if you own a copy of RPG Maker.

    Arguments:
        `duration_per_frame`: The default duration for a single frame for the
            character in milliseconds. Defaults to 200ms.
    """

    duration_per_frame: Millisecond = 200
