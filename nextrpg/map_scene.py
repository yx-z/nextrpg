from pathlib import Path

from pytmx import TiledMap, TiledTileLayer, load_pygame

from nextrpg.character import Character, CharacterSprite
from nextrpg.common_types import Coordinate, Direction, Millesecond
from nextrpg.config import MapConfig
from nextrpg.drawable import Drawable
from nextrpg.event import Event
from nextrpg.scene import Scene


class MapScene(Scene):
    def __init__(
        self, config: MapConfig, tmx_map: Path, player_sprite: CharacterSprite
    ) -> None:
        tile_map = load_pygame(str(tmx_map))
        self.tile_width = tile_map.tilewidth
        self.tile_height = tile_map.tileheight
        self.background_layers = load_layers(
            tile_map, config.background_layer_prefix
        )
        self.foreground_layers = load_layers(
            tile_map, config.foreground_layer_prefix
        )
        self.collision_layers = load_layers(
            tile_map, config.collision_layer_prefix
        )
        self.player = load_player(config, player_sprite, tile_map)

    def event(self, event: Event) -> None:
        pass

    def draw(self, time_delta: Millesecond) -> list[Drawable]:
        return (
            self.draw_layers(self.background_layers)
            + self.player.draw(time_delta)
            + self.draw_layers(self.foreground_layers)
        )

    def draw_layers(self, layers: list[TiledTileLayer]) -> list[Drawable]:
        return [
            Drawable(
                surface=surface,
                coordinate=Coordinate(
                    left=left * self.tile_width, top=top * self.tile_height
                ),
            )
            for layer in layers
            for left, top, surface in layer.tiles()
        ]


def load_layers(tile_map: TiledMap, prefix: str) -> list[TiledTileLayer]:
    return [layer for layer in tile_map.layers if layer.name.startswith(prefix)]


def load_player(
    config: MapConfig, player_sprite_sheet: CharacterSprite, tile_map: TiledMap
) -> Character:
    player = next(
        layer for layer in tile_map if layer.name == config.player_layer
    )[0]
    return Character(
        player_sprite_sheet,
        Coordinate(player.x, player.y),
        Direction[
            player.properties[config.character_direction_property_name].upper()
        ],
    )
