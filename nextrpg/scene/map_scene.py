"""
Map scene implementation.
"""

from dataclasses import dataclass, replace
from functools import cached_property
from itertools import groupby
from pathlib import Path
from typing import NamedTuple, override

from pygame import Surface
from pytmx import (
    TiledMap,
    TiledObjectGroup,
    TiledTileLayer,
    load_pygame,
)

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.config import config
from nextrpg.core import Millisecond, Pixel
from nextrpg.draw_on_screen import (
    Coordinate,
    DrawOnScreen,
    Drawing,
    Rectangle,
    Size,
)
from nextrpg.event.pygame_event import PygameEvent
from nextrpg.scene.scene import Scene

type _LayerIndex = int
type _TiledCoordinate = tuple[int, int]
type _Gid = int | _TiledCoordinate


@dataclass(frozen=True)
class MapScene(Scene):
    """
    A scene implementation that represents a game map loaded from Tiled TMX.

    Handles rendering of map layers, character movement with collisions,
    and proper depth sorting of foreground elements relative to the player.
    """

    _background: list[DrawOnScreen]
    _foreground: list[dict[_Gid, DrawOnScreen]]
    _player: CharacterOnScreen
    _above_character: list[DrawOnScreen]
    _gid_groups: dict[_Gid, set[DrawOnScreen]]

    @classmethod
    def load(cls, tmx_file: Path, player: CharacterDrawing) -> "Scene":
        """
        Load a map scene from a Tiled TMX file.

        Parses the TMX file to extract background layers, foreground elements,
        collision boundaries, and player starting position to construct a
        complete map scene.

        Args:
            `tmx_file`: Path to the Tiled TMX file to load.

            `player`: Character drawing representing the player character.

        Returns:
            `Scene`: A fully initialized map scene.
        """
        return MapScene(
            _draw_layers(
                tmx := load_pygame(str(tmx_file)),
                tile_size := Size(tmx.tilewidth, tmx.tileheight),
                config().map.background,
            ),
            foreground := [
                _get_gid_and_draw(tmx, layer, tile_size)
                for layer in _layers(tmx, config().map.foreground)
            ],
            _player(player, tmx),
            _draw_layers(tmx, tile_size, config().map.above_character),
            _gid_groups(tmx, {k: v for l in foreground for k, v in l.items()}),
        )

    @cached_property
    @override
    def draw_on_screens(self) -> list[DrawOnScreen]:
        """
        Generate the complete list of drawable elements for the map scene.

        Combines background elements, depth-sorted foreground elements with the
        player character, and any debug visuals from the player character.

        Returns:
            `list[DrawOnScreen]`: The complete list of drawable elements in the
            correct rendering order.
        """
        return (
            self._background
            + self._foreground_and_character
            + self._above_character
            + self._player.draw_on_screen.visuals
        )

    @override
    def event(self, event: PygameEvent) -> "Scene":
        """
        Process input events for the map scene.

        Delegates event handling to the player character and returns an
        updated scene with the new player state.

        Args:
            `event`: The pygame event to process.

        Returns:
            `Scene`: The updated scene after processing the event.
        """
        return replace(self, _player=self._player.event(event))

    @override
    def step(self, time_delta: Millisecond) -> "Scene":
        """
        Update the map scene state for a single game step/frame.

        Updates the player character's position and animation state based on the
        elapsed time since the last frame.

        Args:
            `time_delta`: The time that has passed since the last update.

        Returns:
            `Scene`: The updated scene after the time step.
        """
        return replace(self, _player=self._player.step(time_delta))

    @cached_property
    def _foreground_and_character(self) -> list[DrawOnScreen]:
        sorted_by_layer_index_and_bottom = sorted(
            self._layer_gid_draws,
            key=lambda t: _LayerIndexAndBottom(
                t[0], _max_bottom(self._grouped_rectangles(*t[1:]))
            ),
        )
        return [draw for _, _, draw in sorted_by_layer_index_and_bottom]

    @cached_property
    def _layer_gid_draws(self) -> list[tuple[_LayerIndex, _Gid, DrawOnScreen]]:
        foregrounds = list(
            (i, gid, draw)
            for i, gid_to_draws in enumerate(self._foreground)
            for gid, draw in gid_to_draws.items()
        )
        player = (self._player_layer, 0, self._player.draw_on_screen.character)
        return foregrounds + [player]

    @cached_property
    def _player_layer(self) -> _LayerIndex:
        reversed_layers = reversed(list(enumerate(self._foreground)))
        return next(
            (i for i, layer in reversed_layers if self._below_player(layer)), 0
        )

    def _below_player(self, layer: dict[_Gid, DrawOnScreen]) -> bool:
        player = self._player.draw_on_screen.character.visible_rectangle
        return any(
            any(
                player.collide(rect) and rect.bottom < player.bottom
                for rect in self._grouped_rectangles(gid, draw)
            )
            for gid, draw in layer.items()
        )

    def _grouped_rectangles(
        self, gid: _Gid, draw: DrawOnScreen
    ) -> list[Rectangle]:
        return [
            d.visible_rectangle for d in (self._gid_groups.get(gid) or {draw})
        ]


def _max_bottom(rectangles: list[Rectangle]) -> Pixel:
    return max(rectangle.bottom for rectangle in rectangles)


def _draw(
    layer: TiledTileLayer, tile_size: Size
) -> list[tuple[_TiledCoordinate, DrawOnScreen]]:
    return [
        ((coord := (left, top)), _tile(coord, surface, tile_size))
        for left, top, surface in layer.tiles()
    ]


def _tile(coord: _TiledCoordinate, surface: Surface, tile_size) -> DrawOnScreen:
    left, top = coord
    return DrawOnScreen(
        Coordinate(left * tile_size.width, top * tile_size.height),
        Drawing(surface),
    )


def _get_gid_and_draw(
    tmx: TiledMap, layer: TiledTileLayer, tile_size: Size
) -> dict[_Gid, DrawOnScreen]:
    return {
        tmx.tile_properties.get(layer.data[left][top], {}).get(
            "id", (top, left)
        ): draw
        for (top, left), draw in _draw(layer, tile_size)
    }


def _layers(
    tmx: TiledMap, name: str
) -> list[TiledTileLayer | TiledObjectGroup]:
    return [layer for layer in tmx.layers if layer.name.startswith(name)]


def _player(
    character_drawing: CharacterDrawing, tmx: TiledMap
) -> CharacterOnScreen:
    print(f"{tmx=}", end="\n\n\n")
    print(f"{_layers(tmx, config().map.object)=}", end="\n\n\n")
    player = next(
        obj
        for layer in _layers(tmx, config().map.object)
        for obj in layer
        if obj.name == config().map.player
    )
    return CharacterOnScreen(
        character_drawing,
        Coordinate(player.x, player.y),
        speed=player.properties.get(
            config().map.properties.speed, config().character.speed
        ),
        collisions=[
            Rectangle(Coordinate(rect.x, rect.y), Size(rect.width, rect.height))
            for layer in _layers(tmx, config().map.collision)
            for rect in layer
        ],
    )


def _gid_groups(
    tmx: TiledMap, draw_on_screens: dict[_Gid, DrawOnScreen]
) -> dict[_Gid, set[DrawOnScreen]]:
    gid_to_class = {
        tile["id"]: cls
        for tile in tmx.tile_properties.values()
        if (cls := tile.get("type"))
    }
    groups = (
        {gid: draw_on_screens[gid] for gid, _ in gid_group}
        for _, gid_group in groupby(
            sorted(gid_to_class.items(), key=lambda x: x[1]), key=lambda x: x[1]
        )
    )
    return {
        gid: set(gid_to_draw.values())
        for gid_to_draw in groups
        for gid in gid_to_draw
    }


def _draw_layers(
    tmx: TiledMap, tile_size: Size, name: str
) -> list[DrawOnScreen]:
    return [
        draw
        for layer in _layers(tmx, name)
        for _, draw in _draw(layer, tile_size)
    ]


class _LayerIndexAndBottom(NamedTuple):
    layer: _LayerIndex
    bottom: Pixel
