from dataclasses import dataclass

from nextrpg.core.time import Millisecond


@dataclass(frozen=True)
class TimingConfig:
    transition_scene_duration: Millisecond = 800
    animation_duration: Millisecond = 400
