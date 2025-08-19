from dataclasses import dataclass, replace
from functools import cached_property

from nextrpg.core.color import BLACK, Color
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Pixel, Size, Width
from nextrpg.core.time import Millisecond
from nextrpg.global_config.text_config import TextConfig


@dataclass(frozen=True, slots=True)
class SayEventColorBubbleTipConfig:
    base_shift: Width = Width(30)
    tip_shift: Size = Size(40, 40)


@dataclass(frozen=True, slots=True)
class SayEventColorBackgroundConfig:
    background: Color = Color(255, 255, 255, 200)
    border_radius: Pixel = 16
    tip: SayEventColorBubbleTipConfig = SayEventColorBubbleTipConfig()


@dataclass(frozen=True)
class SayEventNineSliceBackgroundConfig:
    background_input: "NineSlice | Callable[[], NineSlice]"
    tip_input: "Drawing | Callable[[],Drawing] | None" = None

    @cached_property
    def background(self) -> "NineSlice":
        if callable(self.background_input):
            return self.background_input()
        return self.background_input

    @cached_property
    def tip(self) -> "Drawing | None":
        if callable(self.tip_input):
            return self.tip_input()
        return self.tip_input


@dataclass(frozen=True)
class SayEventConfig:
    background: (
        SayEventColorBackgroundConfig | SayEventNineSliceBackgroundConfig
    ) = SayEventColorBackgroundConfig()
    add_on_shift: Size = Size(0, 100)
    fade_duration: Millisecond = 200
    padding: Size = Size(12, 12)
    text_delay: Millisecond = 20
    name_override: str | None = None
    scene_coordinate_override: Coordinate | None = None
    character_coordinate_override: Coordinate | None = None
    name_text_config_override: TextConfig | None = None
    text_config_override: TextConfig | None = None
    avatar_input: "Drawing | Callable[[],Drawing] | None" = None

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
        return replace(self.text_config, color=Color(0, 0, 255, 255))
