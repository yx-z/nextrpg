"""
Tile map configuration system for `NextRPG`.

This module provides configuration options for tile map layers and properties
that are created from Tiled Map Editor (TMX) files. It includes the
`TileMapConfig` class which defines layer names and object types for different
rendering and collision purposes.

The tile map configuration features:
- Background layer identification
- Foreground layer identification
- Above-character layer identification
- Collision object identification
- Integration with Tiled Map Editor
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TileMapConfig:
    """
    Configuration class for managing tile map layers and properties.

    This global_config is used by `nextrpg.scene.map_scene.MapScene` to identify
    different types of layers and objects in tile maps created from Tiled Map
    Editor (TMX) files.

    Arguments:
        `background`: Class name of the layer to be identified as background
            layer. Defaults to "background".
        `foreground`: Class name of the layer to be identified as foreground
            layer. Defaults to "foreground".
        `above_character`: Class name of the layer to be rendered above
            characters. Defaults to "above_character".
        `collision`: Class name of the objects to be identified as collision
            objects. Defaults to "collision".
    """

    background: str = "background"
    foreground: str = "foreground"
    above_character: str = "above_character"
    collision: str = "collision"
