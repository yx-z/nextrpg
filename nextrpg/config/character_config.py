from dataclasses import dataclass

from nextrpg.geometry.dimension import (
    HeightScaling,
    PixelPerMillisecond,
    WidthScaling,
)


@dataclass(frozen=True)
class CharacterConfig:
    move_speed: PixelPerMillisecond = 0.2
    bounding_rectangle_scaling: HeightScaling = HeightScaling(0.4)
    start_event_scaling: WidthScaling = WidthScaling(1.2)
