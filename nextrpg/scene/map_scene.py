from dataclasses import dataclass
from itertools import groupby
from pathlib import Path
from typing import override

from pytmx import (
    TiledMap,
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

type _Gid = int


@dataclass(frozen=True)
class MapScene(Scene):
    _background: list[DrawOnScreen]
    _foreground: dict[_Gid, DrawOnScreen]
    _player: CharacterOnScreen
    _tile_size: Size
    _gid_groups: dict[_Gid, dict[_Gid, DrawOnScreen]]

    @classmethod
    def load(cls, tmx_file: Path, player: CharacterDrawing) -> "Scene":
        tmx = load_pygame(str(tmx_file))
        tile_size = Size(tmx.tilewidth, tmx.tileheight)
        return MapScene(
            [
                draw_on_screen
                for layer in _layers(tmx, config().map.background)
                for _, draw_on_screen in _draw(layer, tile_size)
            ],
            foreground := _get_gid_and_draw(
                tmx, _layers(tmx, config().map.foreground), tile_size
            ),
            _player(player, tmx),
            tile_size,
            _gid_groups(tmx, foreground),
        )

    @property
    @override
    def draw_on_screen(self) -> list[DrawOnScreen]:
        character, visuals = self._player.draw_on_screen
        below_character, above_character = partition(
            self._foreground.items(),
            lambda d: self._draw_below_character(d, character),
        )
        return (
            self._background
            + [d for _, d in below_character]
            + [character]
            + visuals
            + [d for _, d in above_character]
        )

    @override
    def event(self, event: PygameEvent) -> "Scene":
        return clone(self, _player=self._player.event(event))

    @override
    def step(self, time_delta: Millisecond) -> "Scene":
        return clone(self, _player=self._player.step(time_delta))

    def _draw_below_character(
        self, tup: tuple[_Gid, DrawOnScreen], character: DrawOnScreen
    ) -> bool:
        gid, draw = tup
        return (
            draw.visible_rectangle.collides(character.visible_rectangle)
            and max(
                draw.visible_rectangle.bottom
                for draw in self._gid_groups.get(gid, {gid: draw}).values()
            )
            < character.visible_rectangle.bottom
        )


def _draw(
    layer: TiledTileLayer, tile_size
) -> list[tuple[Coordinate, DrawOnScreen]]:
    return [
        (
            Coordinate(left, top),
            DrawOnScreen(
                Coordinate(left * tile_size.width, top * tile_size.height),
                Drawing(surface),
            ),
        )
        for left, top, surface in layer.tiles()
    ]


def _get_gid_and_draw(
    tmx: TiledMap, layers: list[TiledTileLayer], tile_size: Size
) -> dict[_Gid, DrawOnScreen]:
    return {
        (
            tmx.get_tile_properties_by_gid(
                gid := layer.data[coord.top][coord.left]
            )
            or {}
        ).get("id", gid): draw
        for layer in layers
        for coord, draw in _draw(layer, tile_size)
    }


def _layers(
    tmx: TiledMap, name: str
) -> list[TiledTileLayer | TiledObjectGroup]:
    return [layer for layer in tmx.layers if layer.name.startswith(name)]


def _player(
    character_drawing: CharacterDrawing, tile_map: TiledMap
) -> CharacterOnScreen:
    player = next(
        obj
        for layer in _layers(tile_map, config().map.object)
        for obj in layer
        if obj.name == config().map.player
    )
    return CharacterOnScreen(
        character_drawing,
        Coordinate(player.x, player.y),
        collisions=[
            Rectangle(Coordinate(rect.x, rect.y), Size(rect.width, rect.height))
            for layer in _layers(tile_map, config().map.collision)
            for rect in layer
        ],
        speed=(
            float(speed)
            if (speed := player.properties.get(config().map.properties.speed))
            else config().character.speed
        ),
    )


def _gid_groups(
    tmx: TiledMap, draw_on_screens: dict[_Gid, DrawOnScreen]
) -> dict[_Gid, dict[_Gid, DrawOnScreen]]:
    gid_to_class = {
        tile["id"]: cls
        for tile in tmx.tile_properties.values()
        if (cls := tile.get("type"))
    }
    gid_groups = (
        {gid: draw_on_screens[gid] for gid, _ in gid_group}
        for _, gid_group in groupby(
            sorted(gid_to_class.items(), key=lambda x: x[1]), key=lambda x: x[1]
        )
    )
    return {gid: group for group in gid_groups for gid in group}
