from dataclasses import dataclass, replace

from nextrpg.core.color import BLACK, WHITE, Rgb, Rgba
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Pixel, Size
from nextrpg.core.time import Millisecond
from nextrpg.global_config.text_config import TextConfig


@dataclass(frozen=True)
class AddOnConfig:
    add_on_shift: Size = Size(0, 100)
    tail_base1_shift: Pixel = 10
    tail_base2_shift: Pixel = 30
    tail_tip_shift: Size = Size(0, 0)


@dataclass(frozen=True)
class SayEventConfig:
    background: Rgba | Rgb = WHITE
    border_radius: Pixel = 16
    fade_duration: Millisecond = 200
    padding: Pixel = 12
    text_delay: Millisecond = 20
    name_color: Rgba | Rgb = Rgba(0, 0, 255, 255)
    add_on: AddOnConfig = AddOnConfig()
    name_override: str | None = None
    coordinate: Coordinate | None = None
    avatar: "Draw | Group | None" = None
    text: TextConfig | None = None

    @property
    def default_text_config(self) -> TextConfig:
        from nextrpg.global_config.global_config import config

        return replace(config().text, color=BLACK)

    @property
    def default_scene_coordinate(self) -> Coordinate:
        from nextrpg.gui.area import screen

        return screen().center

    @property
    def text_config(self) -> TextConfig:
        return self.text or self.default_text_config
