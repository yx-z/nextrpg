from dataclasses import dataclass

from nextrpg.core.dimension import Size
from nextrpg.draw.drawing import Drawing, RectangleDrawing
from nextrpg.draw.drawing_group import DrawingGroup
from nextrpg.global_config.say_event_config import (
    ColorBackgroundConfig,
    NineSliceBackgroundConfig,
)


@dataclass(frozen=True)
class SayEventBubble:
    config: ColorBackgroundConfig | NineSliceBackgroundConfig

    def background(self, size: Size) -> Drawing | DrawingGroup:
        if isinstance(self.config, ColorBackgroundConfig):
            return RectangleDrawing(self.config.background)
