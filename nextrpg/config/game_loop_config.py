from dataclasses import dataclass

from nextrpg.core.time import Millisecond


@dataclass(frozen=True)
class GameLoopConfig:
    max_frames_per_second: int = 120
    garbage_collect_time_threshold: Millisecond | None = 10
