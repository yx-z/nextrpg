from dataclasses import dataclass

from nextrpg.core.time import Millisecond


@dataclass(frozen=True)
class AnimationConfig:
    default_timed_animation_duration: Millisecond = 400
