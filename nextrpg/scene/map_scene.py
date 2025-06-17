from dataclasses import dataclass, replace
from functools import cached_property
from itertools import groupby
from pathlib import Path
from typing import NamedTuple, override

from pytmx import (
    TiledMap,
    TiledObjectGroup,
    TiledTileLayer,
    load_pygame,
)

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.common_types import Millisecond, Pixel
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

type _Gid = int
type _TiledCoordinate = Coordinate


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
            _gid_groups(tmx, {k: v for l in foreground for k, v in l.items()}),
        )

    @cached_property
    @override
    def draw_on_screen(self) -> list[DrawOnScreen]:
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
        sorted_draws = sorted(
            list(
                (layer_index, gid, draw)
                for layer_index, gid_to_draws in enumerate(self._foreground)
                for gid, draw in gid_to_draws.items()
            )
            + [(0, 0, self._player.draw_on_screen.character)],
            key=lambda t: _DepthThenBottom(t[0], self._grouped_bottom(*t[1:])),
        )
        return [draw for _, _, draw in sorted_draws]

    def _grouped_bottom(self, gid: _Gid, draw: DrawOnScreen) -> Pixel:
        return max(
            d.visible_rectangle.bottom
            for d in (self._gid_groups.get(gid) or {draw})
        )


def _draw(
    layer: TiledTileLayer, tile_size: Size
) -> list[tuple[_TiledCoordinate, DrawOnScreen]]:
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
) -> list[dict[_Gid, DrawOnScreen]]:
    return [
        {
            (
                tmx.get_tile_properties_by_gid(
                    gid := layer.data[tiled_coord.top][tiled_coord.left]
                )
                or {}
            ).get("id", gid): draw
            for tiled_coord, draw in _draw(layer, tile_size)
        }
        for layer in layers
    ]


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
        [
            Rectangle(Coordinate(rect.x, rect.y), Size(rect.width, rect.height))
            for layer in _layers(tile_map, config().map.collision)
            for rect in layer
        ],
        (
            float(speed)
            if (speed := player.properties.get(config().map.properties.speed))
            else config().character.speed
        ),
    )


def _gid_groups(
    tmx: TiledMap, draw_on_screens: dict[_Gid, DrawOnScreen]
) -> dict[_Gid, set[DrawOnScreen]]:
    """
    Group drawable elements by their tile type in the Tiled map.

    Creates a mapping from each tile GID to the set of all drawable elements that
    share the same type property, allowing related elements to be treated as a group
    for depth sorting purposes.

    Args:
        tmx: The Tiled map object containing tile properties.

        draw_on_screens: A dictionary mapping tile GIDs to their drawable elements.

    Returns:
        `dict[_Gid, set[DrawOnScreen]]`: A dictionary mapping each tile GID to the
        set of all drawable elements that share the same type.
    """
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
    return {gid: set(group.values()) for group in gid_groups for gid in group}


class _DepthThenBottom(NamedTuple):
    """
    A named tuple used for depth sorting of drawable elements.

    Combines a layer depth value with a bottom coordinate to determine the rendering
    order of elements, with lower depth values appearing behind higher ones and
    elements with lower bottom coordinates appearing behind those with higher ones.

    Args:
        depth: The layer depth value (lower values are drawn first).

        bottom: The bottom coordinate of the element or its group.
    """

    depth: int
    bottom: Pixel
