from dataclasses import dataclass
from nextrpg.model import export


@export
@dataclass(frozen=True)
class TileMapConfig:
    """
    Configuration class for managing tile map layers and properties,
    that is created from tmx files [Tiled](https://www.mapeditor.org/).

    This config is used by `nextrpg.scene.map_scene.MapScene`.

    Attributes:
        `background`:
            Class name of the layer to be identified as background layer.

        `foreground`:
            Class name of the layer to be identified as foreground layer.

        `collision`:
            Class name of the objects to be identified as collision objects.
    """

    background: str = "background"
    foreground: str = "foreground"
    above_character: str = "above_character"
    collision: str = "collision"
