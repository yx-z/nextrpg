from collections.abc import Callable
from dataclasses import dataclass, replace
from enum import Enum, auto
from functools import cached_property
from typing import TYPE_CHECKING

from nextrpg.config.drawing.text_config import TextConfig
from nextrpg.core.time import Millisecond
from nextrpg.drawing.color import BLACK, BLUE, Color
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Pixel
from nextrpg.geometry.size import Height, Size, Width

if TYPE_CHECKING:
    from nextrpg.drawing.drawing import Drawing
    from nextrpg.drawing.nine_slice import NineSlice
    from nextrpg.drawing.sprite import Sprite


@dataclass(frozen=True)
class SayEventColorBackgroundConfig:
    color: Color = Color(255, 255, 255, 200)
    border_radius: Pixel = 10
    tip_height: Height = Height(20)
    tip_width1: Width = Width(10)
    tip_width2: Width = Width(30)

    @cached_property
    def tip_at_top(self) -> Drawing:
        from nextrpg.drawing.polygon_drawing import PolygonDrawing
        from nextrpg.geometry.coordinate import ORIGIN

        point1 = ORIGIN + self.tip_height + self.tip_width1
        point2 = ORIGIN + self.tip_height + self.tip_width2
        points = (ORIGIN, point1, point2)
        poly = PolygonDrawing(points, self.color)
        return poly.drawing

    @cached_property
    def tip_at_bottom(self) -> Drawing:
        return self.tip_at_top.flip(vertical=True)


@dataclass(frozen=True)
class SayEventNineSliceBackgroundConfig:
    nine_slice_input: NineSlice | Callable[[], NineSlice]
    tip_at_top_input: Sprite | Callable[[], Sprite]
    tip_at_bottom_input: Sprite | Callable[[], Sprite] | None = None

    @cached_property
    def nine_slice(self) -> NineSlice:
        if callable(self.nine_slice_input):
            return self.nine_slice_input()
        return self.nine_slice_input

    @cached_property
    def tip_at_top(self) -> Sprite:
        if callable(self.tip_at_top_input):
            return self.tip_at_top_input()
        return self.tip_at_top_input

    @cached_property
    def tip_at_bottom(self) -> Sprite:
        if self.tip_at_bottom_input is None:
            return self.tip_at_top.flip(vertical=True)
        if callable(self.tip_at_bottom_input):
            return self.tip_at_bottom_input()
        return self.tip_at_bottom_input


class AvatarPosition(Enum):
    LEFT = auto()
    RIGHT = auto()


@dataclass(frozen=True)
class SayEventConfig:
    background: (
        SayEventColorBackgroundConfig | SayEventNineSliceBackgroundConfig
    ) = SayEventColorBackgroundConfig()
    character_position_to_add_on_edge_center: Size = Size(5, 0)
    background_edge_center_to_tip: Width = Width(5)
    fade_duration: Millisecond = 200
    padding: Size = Size(12, 12)
    text_delay: Millisecond = 15
    name_override: str | None = None
    scene_coordinate_input: Coordinate | None = None
    character_coordinate_input: Coordinate | None = None
    name_text_config_input: TextConfig | None = None
    text_config_input: TextConfig | None = None
    avatar_input: Sprite | Callable[[], Sprite] | None = None
    avatar_position: AvatarPosition = AvatarPosition.LEFT

    @cached_property
    def avatar(self) -> Sprite | None:
        if callable(self.avatar_input):
            return self.avatar_input()
        return self.avatar_input

    @cached_property
    def scene_coordinate(self) -> Coordinate:
        if self.scene_coordinate_input:
            return self.scene_coordinate_input

        from nextrpg.gui.screen_area import screen_area

        return screen_area().center

    @cached_property
    def text_config(self) -> TextConfig:
        if self.text_config_input:
            return self.text_config_input

        from nextrpg.config.config import config

        text_config = config().drawing.text
        return replace(text_config, color=BLACK)

    @cached_property
    def name_text_config(self) -> TextConfig:
        if self.name_text_config_input:
            return self.name_text_config_input
        return replace(self.text_config, color=BLUE)
