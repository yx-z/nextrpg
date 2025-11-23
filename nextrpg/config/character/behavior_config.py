from dataclasses import dataclass

from nextrpg.geometry.dimension import (
    PixelPerMillisecond,
)
from nextrpg.geometry.scaling import HeightScaling, WidthScaling


@dataclass(frozen=True)
class BehaviorConfig:
    move_speed: PixelPerMillisecond = 0.2
    bounding_rectangle_scaling: HeightScaling = HeightScaling(0.4)
    start_event_scaling: WidthScaling = WidthScaling(1.2)
