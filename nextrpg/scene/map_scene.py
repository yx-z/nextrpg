from dataclasses import dataclass
from pathlib import Path
from typing import override

from pytmx import (
    TiledMap,
    TiledObject,
    TiledObjectGroup,
    TiledTileLayer,
    load_pygame,
)

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.common_types import Millisecond
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
from nextrpg.util import clone, partition


@dataclass(frozen=True)
class MapScene(Scene):
    _background: list[DrawOnScreen]
    _foreground: list[DrawOnScreen]
    _player: CharacterOnScreen
    _tile_size: Size

    @classmethod
    def load(cls, tmx_file: Path, player: CharacterDrawing) -> "Scene":
        tmx = load_pygame(str(tmx_file))
        tile_size = Size(tmx.tilewidth, tmx.tileheight)
        return MapScene(
            _draw(_load_layers(tmx, config().map.background), tile_size),
            _draw(_load_layers(tmx, config().map.foreground), tile_size),
            _load_player(player, tmx),
            tile_size,
        )

    @property
    @override
    def draw_on_screen(self) -> list[DrawOnScreen]:
        character, visuals = self._player.draw_on_screen
        below_character, above_character = partition(
            self._foreground,
            lambda d: d.visible_rectangle.bottom
            < character.visible_rectangle.bottom,
        )
        return (
            self._background
            + below_character
            + [character]
            + visuals
            + above_character
        )

    @override
    def event(self, event: PygameEvent) -> "Scene":
        return clone(self, _player=self._player.event(event))

    @override
    def step(self, time_delta: Millisecond) -> "Scene":
        return clone(self, _player=self._player.step(time_delta))


def _draw(layers: list[TiledTileLayer], tile_size: Size) -> list[DrawOnScreen]:
    return [
        DrawOnScreen(
            Coordinate(left * tile_size.width, top * tile_size.height),
            Drawing(surface),
        )
        for layer in layers
        for left, top, surface in layer.tiles()
    ]


def _load_layers(
    tile_map: TiledMap, name: str
) -> list[TiledTileLayer | TiledObjectGroup]:
    return [layer for layer in tile_map.layers if layer.name.startswith(name)]


def _load_player(
    character_drawing: CharacterDrawing, tile_map: TiledMap
) -> CharacterOnScreen:
    player: TiledObject = next(
        obj
        for layer in _load_layers(tile_map, config().map.object)
        for obj in layer
        if obj.name == config().map.player
    )
    return CharacterOnScreen(
        character_drawing,
        Coordinate(player.x, player.y),
        collisions=[
            Rectangle(Coordinate(rect.x, rect.y), Size(rect.width, rect.height))
            for layer in _load_layers(tile_map, config().map.collision)
            for rect in layer
        ],
        speed=(
            float(speed)
            if (speed := player.properties.get(config().map.properties.speed))
            else config().character.speed
        ),
    )
