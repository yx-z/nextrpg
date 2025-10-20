from dataclasses import dataclass


@dataclass(frozen=True)
class GameLoopConfig:
    max_frames_per_second: int = 60
