from dataclasses import dataclass

from nextrpg.core import Millisecond
from nextrpg.model import export


@export
@dataclass(frozen=True)
class RpgMakerCharacterDrawingConfig:
    """
    Configuration class for RPG Maker character drawings.

    This config is used by
    `nextrpg.character.rpg_maker_drawing.RpgMakerCharacterDrawing`
    to control how character sprites are animated and displayed. It defines the
    animation timing, idle behavior, and default orientation.

    Note that `nextrpg` is only compatible with the RPG Maker character
    sprite sheet format to be able to re-use existing resources.

    However, using RPG Maker's
    [Runtime Time Package (RTP)](https://www.rpgmakerweb.com/run-time-package)
    in non-RPG Maker framework violates the license of RPG Maker,
    even if you own a copy of RPG Maker.

    Attributes:
        `frame_duration`: The default duration for a single frame for
            the character.
    """

    duration_per_frame: Millisecond = 200
