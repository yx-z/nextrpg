"""
Resource configuration system for `NextRPG`.

This module provides configuration options for resource management in
`NextRPG` games. It includes the `ResourceConfig` class which defines caching
parameters for various game resources.

The resource configuration features:
- Map scene caching configuration
- Drawing resource caching configuration
- Memory management for game resources
- Performance optimization settings
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceConfig:
    """
    Configuration class for resource loading and caching.

    This global_config defines caching parameters for various game resources to
    optimize memory usage and performance.

    Arguments:
        `map_cache_size`: The maximum number of map scenes to cache in memory.
            Defaults to 8.
        `drawing_cache_size`: The maximum number of drawing resources to cache
            in memory. Defaults to 8.
    """

    map_cache_size: int = 8
    drawing_cache_size: int = 8
