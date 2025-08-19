from dataclasses import dataclass

from nextrpg.core.color import Color
from nextrpg.core.dimension import HeightScaling
from nextrpg.core.time import Millisecond


@dataclass(frozen=True, slots=True)
class CutsceneConfig:
    background_override: Color | None = None
    screen_height_scaling: HeightScaling = HeightScaling(0.1)
    wait: bool = True
    duration_override: Millisecond | None = None

    @property
    def background(self) -> Color:
        from nextrpg.global_config.global_config import config

        return self.background_override or config().window.background

    @property
    def duration(self) -> Millisecond:
        from nextrpg.global_config.global_config import config

        return self.duration_override or config().transition.duration
