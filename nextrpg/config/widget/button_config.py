from dataclasses import dataclass

from nextrpg.config.drawing.text_config import TextConfig
from nextrpg.core.time import Millisecond
from nextrpg.drawing.color import WHITE, Color
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.dimension import Pixel
from nextrpg.geometry.padding import Padding, padding_for_all_sides


@dataclass(frozen=True)
class ButtonConfig:
    padding: Padding = padding_for_all_sides(10)
    text_config_input: TextConfig | None = None
    fade_duration_input: Millisecond | None = None
    border_width: Pixel = 2
    border_radius: Pixel = 5
    background_color: Color = WHITE.with_percentage_alpha(0.7)
    border_color: Color = WHITE
    anchor: Anchor = Anchor.TOP_LEFT

    @property
    def fade_duration(self) -> Millisecond:
        from nextrpg.config.config import config

        if self.fade_duration_input is None:
            return config().timing.animation_duration
        return self.fade_duration_input

    @property
    def text_config(self) -> TextConfig:
        if self.text_config_input:
            return self.text_config_input

        from nextrpg.config.config import config

        return config().text
