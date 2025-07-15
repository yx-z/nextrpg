"""
Resource configuration system for NextRPG.

This module provides configuration options for resource management
in NextRPG games. It includes the `ResourceConfig` class which
defines caching parameters for various game resources.

The resource configuration features:
- Map scene caching configuration
- Drawing resource caching configuration
- Memory management for game resources
- Performance optimization settings

Example:
    ```python
    from nextrpg.resource_config import ResourceConfig

    # Create default resource config
    config = ResourceConfig()

    # Create custom resource config
    custom_config = ResourceConfig(
        map_cache_size=16,
        drawing_cache_size=32
    )
    ```
"""

from dataclasses import dataclass

from nextrpg.model import export


@export
@dataclass(frozen=True)
class ResourceConfig:
    """
    Configuration class for resource loading and caching.

    This config defines caching parameters for various game resources
    to optimize memory usage and performance.

    Arguments:
        `map_cache_size`: The maximum number of map scenes to cache
            in memory. Defaults to 8.

        `drawing_cache_size`: The maximum number of drawing resources
            to cache in memory. Defaults to 8.

    Example:
        ```python
        from nextrpg.resource_config import ResourceConfig

        # Default configuration
        config = ResourceConfig()

        # High memory configuration
        high_mem_config = ResourceConfig(
            map_cache_size=32,
            drawing_cache_size=64
        )

        # Low memory configuration
        low_mem_config = ResourceConfig(
            map_cache_size=4,
            drawing_cache_size=4
        )
        ```
    """

    map_cache_size: int = 8
    drawing_cache_size: int = 8
