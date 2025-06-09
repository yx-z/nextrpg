from pathlib import Path
from typing import Final, override

from pytmx import TiledMap, TiledTileLayer, load_pygame

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.common_types import Direction, Millisecond
from nextrpg.config import config
from nextrpg.draw_on_screen import (
    Coordinate,
    DrawOnScreen,
    Drawing,
    Rectangle,
    Size,
)
from nextrpg.event.pygame_event import PygameEvent
from nextrpg.scene.scene import Scene
from nextrpg.util import partition


class MapScene(Scene):
    def __init__(self, tmx_map: Path, player_sprite: CharacterDrawing) -> None:
        tile_map = load_pygame(str(tmx_map))
        self._tile_size: Final[Size] = Size(
            tile_map.tilewidth, tile_map.tileheight
        )
        self._background: Final[list[DrawOnScreen]] = self._draw_layers(
            _load_layers(tile_map, config().map.background_layer_prefix)
        )
        self._foreground: Final[list[DrawOnScreen]] = self._draw_layers(
            _load_layers(tile_map, config().map.foreground_layer_prefix)
        )
        self._player: Final[CharacterOnScreen] = _load_player(
            player_sprite, tile_map
        )

    @override
    def event(self, event: PygameEvent) -> None:
        self._player.event(event)

    @override
    def draw_on_screen(self, time_delta: Millisecond) -> list[DrawOnScreen]:
        character, visuals = self._player.draw_on_screen(time_delta)
        below_character, above_character = partition(
            self._foreground,
            lambda d: d.visual_bottom < character.rectangle.bottom
            and d.rectangle.collides(character.rectangle),
        )
        return (
            self._background
            + below_character
            + [character]
            + visuals
            + above_character
        )

    def _draw_layers(self, layers: list[TiledTileLayer]) -> list[DrawOnScreen]:
        return [
            DrawOnScreen(
                Coordinate(
                    left * self._tile_size.width, top * self._tile_size.height
                ),
                Drawing(surface),
            )
            for layer in layers
            for left, top, surface in layer.tiles()
        ]


def _load_layers(tile_map: TiledMap, prefix: str) -> list[TiledTileLayer]:
    return [layer for layer in tile_map.layers if layer.name.startswith(prefix)]


def _load_player(
    sprite_sheet: CharacterDrawing, tile_map: TiledMap
) -> CharacterOnScreen:
    player = next(
        obj
        for layer in _load_layers(tile_map, config().map.object_layer_prefix)
        for obj in layer
        if obj.name == config().map.player_object
    )
    return CharacterOnScreen(
        sprite_sheet,
        Coordinate(player.x, player.y),
        Direction[
            player.properties[config().map.properties.character_direction]
        ],
        collisions=[
            Rectangle(Coordinate(rect.x, rect.y), Size(rect.width, rect.height))
            for layer in _load_layers(
                tile_map, config().map.collision_layer_prefix
            )
            for rect in layer
        ],
        speed=player.properties.get(config().map.properties.character_speed),
    )
