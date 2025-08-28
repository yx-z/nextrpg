from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DrawingConfig:
    cache_size: int = 8
