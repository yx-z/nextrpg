from dataclasses import dataclass, replace
from functools import cached_property

from nextrpg.text_config import TextConfig
from nextrpg.core import BLACK, Millisecond, Pixel, Rgba, WHITE
from nextrpg.model import export


@export
@dataclass(frozen=True)
class SayEventConfig:
    background: Rgba = WHITE
    border_radius: Pixel = 20
    padding: Pixel = 16
    fade_duration: Millisecond = 200

    @cached_property
    def text(self) -> TextConfig:
        from nextrpg.global_config import config

        return replace(config().text, color=BLACK)
