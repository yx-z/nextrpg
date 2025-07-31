from dataclasses import dataclass

from nextrpg.core.dimension import PixelPerMillisecond


@dataclass(frozen=True)
class CharacterConfig:
    move_speed: PixelPerMillisecond = 0.2
