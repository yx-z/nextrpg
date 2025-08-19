from dataclasses import dataclass

from nextrpg.core.coordinate import ORIGIN
from nextrpg.core.dimension import Height, Size
from nextrpg.draw.drawing import (
    Drawing,
    PolygonDrawing,
    RectangleDrawing,
)
from nextrpg.draw.drawing_group import DrawingGroup
from nextrpg.global_config.say_event_config import (
    SayEventColorBackgroundConfig,
    SayEventNineSliceBackgroundConfig,
)


@dataclass(frozen=True)
class SayEventColorBubble:
    config: SayEventColorBackgroundConfig

    def background(self, size: Size) -> Drawing | DrawingGroup:
        return RectangleDrawing(
            size, self.config.background, self.config.border_radius
        )

    def tip(self, tip_height: Height) -> PolygonDrawing | None:
        if not self.config.tip:
            return None
        base = ORIGIN + self.config.tip.base_shift
        tip = ORIGIN + self.config.tip.tip_shift + tip_height
        points = (ORIGIN, base, tip)
        return PolygonDrawing(points, self.config.background)


@dataclass(frozen=True)
class SayEventNineSliceBubble:
    config: SayEventNineSliceBackgroundConfig
    is_character: bool

    def background(self, size: Size) -> Drawing | DrawingGroup:
        return self.config.background.stretch(size)

    def tip(self, tip_height: Height) -> Drawing | None:
        if not self.config.tip:
            return None
