from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceConfig:
    tmx_cache_size: int = 8
    map_scene_cache_size: int = 8
    sound_cache_size: int = 8
    drawing_cache_size: int = 128
