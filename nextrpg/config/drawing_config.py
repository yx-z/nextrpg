from dataclasses import dataclass


@dataclass(frozen=True)
class DrawingConfig:
    cache_size: int = 8
