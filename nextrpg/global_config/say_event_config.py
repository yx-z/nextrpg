from dataclasses import dataclass, replace

from nextrpg.core.color import BLACK, Color
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Pixel, Size, Width
from nextrpg.core.time import Millisecond
from nextrpg.global_config.text_config import TextConfig


@dataclass(frozen=True)
class AddOnConfig:
    add_on_shift: Size = Size(0, 100)
    tail_base1_shift: Width = Width(10)
    tail_base2_shift: Width = Width(30)
    tail_tip_shift: Size = Size(0, 0)


@dataclass(frozen=True)
class SayEventConfig:
    background: Color = Color(255, 255, 255, 200)
    border_radius: Pixel = 16
    fade_duration: Millisecond = 200
    padding: Size = Size(12, 12)
    text_delay: Millisecond = 20
    add_on: AddOnConfig = AddOnConfig()
    name_override: str | None = None
    scene_coordinate_override: Coordinate | None = None
    character_coordinate_override: Coordinate | None = None
    name_text_config_override: TextConfig | None = None
    text_config_override: TextConfig | None = None
    avatar: "Drawing | DrawingGroup | None" = None

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
