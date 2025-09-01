from collections.abc import Callable
from dataclasses import dataclass, replace
from functools import cached_property
from typing import TYPE_CHECKING

from nextrpg.config.text_config import TextConfig
from nextrpg.core.time import Millisecond
from nextrpg.draw.color import BLACK, BLUE, Color
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Height, Pixel, Size, Width

if TYPE_CHECKING:
    from nextrpg.draw.drawing import Drawing
    from nextrpg.draw.drawing_group import DrawingGroup
    from nextrpg.draw.nine_slice import NineSlice


@dataclass(frozen=True)
class SayEventColorBackgroundConfig:
    color: Color = Color(255, 255, 255, 200)
    border_radius: Pixel = 10
    tip_height: Height = Height(20)
    tip_width1: Width = Width(10)
    tip_width2: Width = Width(30)

    @cached_property
    def tip_at_top(self) -> Drawing:
        from nextrpg.draw.polygon_drawing import PolygonDrawing
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
    tip_at_top_input: Drawing | Callable[[], Drawing]
    tip_at_bottom_input: Drawing | Callable[[], Drawing] | None = None

    @cached_property
    def nine_slice(self) -> NineSlice:
        if callable(self.nine_slice_input):
            return self.nine_slice_input()
        return self.nine_slice_input

    @cached_property
    def tip_at_top(self) -> Drawing:
        if callable(self.tip_at_top_input):
            return self.tip_at_top_input()
        return self.tip_at_top_input

    @cached_property
    def tip_at_bottom(self) -> Drawing:
        if self.tip_at_bottom_input is None:
            return self.tip_at_top.flip(vertical=True)
        if callable(self.tip_at_bottom_input):
            return self.tip_at_bottom_input()
        return self.tip_at_bottom_input


@dataclass(frozen=True)
class SayEventConfig:
    background: (
        SayEventColorBackgroundConfig | SayEventNineSliceBackgroundConfig
    ) = SayEventColorBackgroundConfig()
    character_position_to_add_on_edge_center: Size = Size(10, 10)
    background_edge_center_to_tip: Width = Width(5)
    fade_duration: Millisecond = 200
    padding: Size = Size(12, 12)
    text_delay: Millisecond = 20
    name_override: str | None = None
    scene_coordinate_override: Coordinate | None = None
    character_coordinate_override: Coordinate | None = None
    name_text_config_override: TextConfig | None = None
    text_config_override: TextConfig | None = None
    avatar_input: (
        Drawing
        | DrawingGroup
        | Callable[[], Drawing]
        | Callable[[], DrawingGroup]
        | None
    ) = None

    @cached_property
    def avatar(self) -> Drawing | DrawingGroup | None:
        if callable(self.avatar_input):
            return self.avatar_input()
        return self.avatar_input

    @property
    def scene_coordinate(self) -> Coordinate:
        if self.scene_coordinate_override:
            return self.scene_coordinate_override

        from nextrpg.ui.area import screen

        return screen().center

    @property
    def text_config(self) -> TextConfig:
        if self.text_config_override:
            return self.text_config_override

        from nextrpg.config.config import config

        return replace(config().text, color=BLACK)

    @property
    def name_text_config(self) -> TextConfig:
        if self.name_text_config_override:
            return self.name_text_config_override
        return replace(self.text_config, color=BLUE)
