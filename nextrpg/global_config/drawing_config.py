from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DrawingConfig:
    cache_size: int = 8
    smooth_scale: bool = True
    smooth_line: bool = True
