from dataclasses import dataclass

from nextrpg.model import export


@export
@dataclass(frozen=True)
class ResourceConfig:
    """
    Configuration class for resource loading.

    Attributes:
        `map_cache_size`: The maximum number of map scenes to cache in memory.
    """

    map_cache_size: int = 8
    drawing_cache_size: int = 8
