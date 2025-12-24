from dataclasses import dataclass
from functools import cached_property

from nextrpg.core.time import Millisecond
from nextrpg.drawing.color import Color
from nextrpg.geometry.scaling import HeightScaling


@dataclass(frozen=True)
class CutsceneConfig:
    background_override: Color | None = None
    cover_from_screen_scaling: HeightScaling = HeightScaling(0.1)
    wait: bool = True
    duration_override: Millisecond | None = None

    @cached_property
    def background(self) -> Color:
        from nextrpg.config.config import config

        return self.background_override or config().system.window.background

    @cached_property
    def duration(self) -> Millisecond:
        from nextrpg.config.config import config

        return (
            self.duration_override
            or config().animation.default_timed_animation_duration
        )
