from dataclasses import dataclass

from nextrpg.core.time import Millisecond


@dataclass(frozen=True, slots=True)
class GameLoopConfig:
    max_frames_per_second: int = 60
    garbage_collect_time_threshold: Millisecond | None = 10
