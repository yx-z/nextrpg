from dataclasses import dataclass

from nextrpg.core.time import Millisecond


@dataclass(frozen=True)
class TimingConfig:
    transition_total_duration: Millisecond = 800
    fade_duration: Millisecond = 350
