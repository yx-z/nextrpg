from collections.abc import Callable
from dataclasses import dataclass, replace
from functools import cached_property
from typing import TYPE_CHECKING

from nextrpg.core.color import BLACK, BLUE, Color
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Pixel, Size, Width
from nextrpg.core.time import Millisecond
from nextrpg.global_config.text_config import TextConfig

if TYPE_CHECKING:
    from nextrpg.draw.drawing import Drawing
    from nextrpg.draw.nine_slice import NineSlice
    from nextrpg.draw.polygon import PolygonDrawing


@dataclass(frozen=True, slots=True)
class SayEventColorBackgroundTipConfig:
    base_shift: Width = Width(30)
    tip_shift: Size = Size(40, 40)


@dataclass(frozen=True)
class SayEventColorBackgroundConfig:
    background: Color = Color(255, 255, 255, 200)
    border_radius: Pixel = 16
    tip_config: SayEventColorBackgroundTipConfig | None = (
        SayEventColorBackgroundTipConfig()
    )

    @cached_property
    def tip(self) -> PolygonDrawing | None:
        if not self.tip_config:
            return None

        from nextrpg.core.coordinate import ORIGIN
        from nextrpg.draw.polygon import PolygonDrawing

        base = ORIGIN + self.tip_config.base_shift
        tip = ORIGIN + self.tip_config.tip_shift
        points = (ORIGIN, base, tip)
        return PolygonDrawing(points, self.background)


@dataclass(frozen=True)
class SayEventNineSliceBackgroundConfig:
    nine_slice_input: NineSlice | Callable[[], NineSlice]
    tip_input: Drawing | Callable[[], Drawing] | None = None

    @cached_property
    def nine_slice(self) -> NineSlice:
        if callable(self.nine_slice_input):
            return self.nine_slice_input()
        return self.nine_slice_input

    @cached_property
    def tip(self) -> Drawing | None:
        if callable(self.tip_input):
            return self.tip_input()
        return self.tip_input


@dataclass(frozen=True)
class SayEventConfig:
    background: (
        SayEventColorBackgroundConfig | SayEventNineSliceBackgroundConfig
    ) = SayEventColorBackgroundConfig()
    background_min_size: Size | None = None
    character_position_to_add_on_bottom: Size = Size(0, 100)
    fade_duration: Millisecond = 200
    padding: Size = Size(12, 12)
    text_delay: Millisecond = 20
    name_override: str | None = None
    scene_coordinate_override: Coordinate | None = None
    character_coordinate_override: Coordinate | None = None
    name_text_config_override: TextConfig | None = None
    text_config_override: TextConfig | None = None
    avatar_input: Drawing | Callable[[], Drawing] | None = None

    @cached_property
    def avatar(self) -> "Drawing":
        if callable(self.avatar_input):
            return self.avatar_input()
        return self.avatar_input

    @property
    def scene_coordinate(self) -> Coordinate:
        if self.scene_coordinate_override:
            return self.scene_coordinate_override

        from nextrpg.gui.area import screen

        return screen().center

    @property
    def text_config(self) -> TextConfig:
        if self.text_config_override:
            return self.text_config_override

        from nextrpg.global_config.global_config import config

        return replace(config().text, color=BLACK)

    @property
    def name_text_config(self) -> TextConfig:
        if self.name_text_config_override:
            return self.name_text_config_override
        return replace(self.text_config, color=BLUE)
