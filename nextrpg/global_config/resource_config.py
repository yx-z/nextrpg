from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceConfig:
    map_cache_size: int = 8
    draw_cache_size: int = 8
