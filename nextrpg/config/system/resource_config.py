from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceConfig:
    tmx_loader_cache_size: int = 16
    map_scene_cache_size: int = 8
    sound_cache_size: int = 8
    save_slot_cache_size: int = 8
    drawing_cache_size: int = 8192
    background_thread_count: int = 4
