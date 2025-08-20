from dataclasses import dataclass
from functools import cached_property

from nextrpg.core.coordinate import ORIGIN
from nextrpg.core.dimension import Size
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

    @cached_property
    def tip(self) -> PolygonDrawing | None:
        if not self.config.tip:
            return None
        base = ORIGIN + self.config.tip.base_shift
        tip = ORIGIN + self.config.tip.tip_shift
        points = (ORIGIN, base, tip)
        return PolygonDrawing(points, self.config.background)


@dataclass(frozen=True)
class SayEventNineSliceBubble:
    config: SayEventNineSliceBackgroundConfig

    def background(self, size: Size) -> Drawing | DrawingGroup:
        return self.config.background.stretch(size)

    @cached_property
    def tip(self) -> Drawing | None:
        return self.config.tip
