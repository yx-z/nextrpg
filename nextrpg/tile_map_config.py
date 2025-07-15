"""
Tile map configuration system for NextRPG.

This module provides configuration options for tile map layers and
properties that are created from Tiled Map Editor (TMX) files.
It includes the `TileMapConfig` class which defines layer names
and object types for different rendering and collision purposes.

The tile map configuration features:
- Background layer identification
- Foreground layer identification
- Above-character layer identification
- Collision object identification
- Integration with Tiled Map Editor

Example:
    ```python
    from nextrpg.tile_map_config import TileMapConfig

    # Create default tile map config
    config = TileMapConfig()

    # Create custom tile map config
    custom_config = TileMapConfig(
        background="bg",
        foreground="fg",
        above_character="above",
        collision="solid"
    )
    ```
"""

from dataclasses import dataclass

from nextrpg.model import export


@export
@dataclass(frozen=True)
class TileMapConfig:
    """
    Configuration class for managing tile map layers and properties.

    This config is used by `nextrpg.scene.map_scene.MapScene` to
    identify different types of layers and objects in tile maps
    created from Tiled Map Editor (TMX) files.

    Arguments:
        `background`: Class name of the layer to be identified as
            background layer. Defaults to "background".

        `foreground`: Class name of the layer to be identified as
            foreground layer. Defaults to "foreground".

        `above_character`: Class name of the layer to be rendered
            above characters. Defaults to "above_character".

        `collision`: Class name of the objects to be identified as
            collision objects. Defaults to "collision".

    Example:
        ```python
        from nextrpg.tile_map_config import TileMapConfig

        # Default configuration
        config = TileMapConfig()

        # Custom configuration for specific map
        custom_config = TileMapConfig(
            background="Background",
            foreground="Foreground",
            above_character="AbovePlayer",
            collision="Solid"
        )
        ```
    """

    background: str = "background"
    foreground: str = "foreground"
    above_character: str = "above_character"
    collision: str = "collision"
