from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from itertools import product
from typing import NamedTuple, Self

from pytmx import TiledObject, TiledTileLayer

from nextrpg.animation.animation_on_screen import AnimationOnScreen
from nextrpg.animation.animation_on_screens import AnimationOnScreens
from nextrpg.animation.cyclic_animation import CyclicAnimation
from nextrpg.animation.cyclic_animation_on_screen import CyclicAnimationOnScreen
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.npc_on_screen import NpcOnScreen
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.log import Log
from nextrpg.core.time import Millisecond
from nextrpg.core.tmx_loader import TmxLoader, get_geometry, is_rect
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.geometry.coordinate import Coordinate, YAxis
from nextrpg.geometry.dimension import Size
from nextrpg.geometry.polygon_area_on_screen import PolygonAreaOnScreen
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen

log = Log()


@dataclass(frozen=True)
class TileGroup:
    index: int
    tile: AnimationOnScreens
    visible_bottom: YAxis

    def __lt__(self, other: Self) -> bool:
        if self.index == other.index:
            return self.visible_bottom < other.visible_bottom
        return self.index < other.index

    def tick(self, time_delta: Millisecond) -> Self:
        tile = self.tile.tick(time_delta)
        return replace(self, tile=tile)


@dataclass(frozen=True)
class ForegroundLayer:
    index: int
    tiles: tuple[TileGroup, ...]

    def tick(self, time_delta: Millisecond) -> Self:
        tiles = tuple(tile.tick(time_delta) for tile in self.tiles)
        return replace(self, tiles=tiles)


@dataclass(frozen=True)
class ForegroundLayers:
    layers: tuple[ForegroundLayer, ...]

    def tick(self, time_delta: Millisecond) -> Self:
        layers = tuple(layer.tick(time_delta) for layer in self.layers)
        return replace(self, layers=layers)

    def drawing_on_screens(
        self, player: PlayerOnScreen, npcs: tuple[NpcOnScreen, ...]
    ) -> tuple[DrawingOnScreen, ...]:
        characters = (player,) + npcs
        character_layers = tuple(
            self._character_layer(character) for character in characters
        )
        all_tiles = tuple(tile for layer in self.layers for tile in layer.tiles)
        tiles = sorted(all_tiles + character_layers)
        return tuple(
            drawing_on_screen
            for tile in tiles
            for drawing_on_screen in tile.tile.drawing_on_screens
        )

    def _character_layer(self, character: CharacterOnScreen) -> TileGroup:
        index = self._layer_index(character)
        log.debug(t"{character.name} layered at {index}", duration=None)
        resource = AnimationOnScreens(character.drawing_on_screens)
        return TileGroup(
            index,
            resource,
            character.drawing_on_screen.visible_rectangle_area_on_screen.bottom,
        )

    def _layer_index(self, character: CharacterOnScreen) -> int:
        for i, layer in enumerate(self.layers):
            if _below_character_layer(character, layer):
                return i + 1
        return 0


@dataclass_with_default(frozen=True)
class MapLoader(TmxLoader):
    _: KW_ONLY = private_init_below()
    background: AnimationOnScreens = default(
        lambda self: self._draw_layers(config().map.background)
    )
    foregrounds: ForegroundLayers = default(lambda self: self._init_foregrounds)
    above_character: AnimationOnScreens = default(
        lambda self: self._draw_layers(config().map.above_character)
    )
    collisions: tuple[PolygonAreaOnScreen, ...] = default(
        lambda self: self._init_collisions
    )
    collision_visuals: tuple[DrawingOnScreen, ...] = default(
        lambda self: self._init_collision_visuals
    )

    def tick(self, time_delta: Millisecond) -> Self:
        background = self.background.tick(time_delta)
        foregrounds = self.foregrounds.tick(time_delta)
        above_character = self.above_character.tick(time_delta)
        return replace(
            self,
            background=background,
            foregrounds=foregrounds,
            above_character=above_character,
        )

    @cached_property
    def map_size(self) -> Size:
        width = self._tmx.width * self._tile_size.width
        height = self._tmx.height * self._tile_size.height
        return width * height

    @property
    def _init_colliders(self) -> tuple[_Collider, ...]:
        return tuple(
            _Collider(_TileCoordinate(x, y), collider)
            for layer in self._all_tile_layers
            for x, y, gid in layer
            for collider in self._collider(gid)
        )

    def _collider(self, gid: _Gid) -> tuple[TiledObject, ...]:
        return tuple(
            self._tmx.tile_properties.get(gid, {}).get("colliders", ())
        )

    def _polygon(
        self, coordinate: _TileCoordinate, obj: TiledObject
    ) -> PolygonAreaOnScreen:
        return self._from_rect(coordinate, obj) or self._from_points(
            coordinate, obj
        )

    def _from_points(
        self, coordinate: _TileCoordinate, obj: TiledObject
    ) -> PolygonAreaOnScreen:
        w, h = self._tile_size
        cx, cy = coordinate
        return PolygonAreaOnScreen(
            tuple(Coordinate(cx * w + x, cy * h + y) for x, y in obj.as_points)
        )

    def _from_rect(
        self, coordinate: _TileCoordinate, obj: TiledObject
    ) -> RectangleAreaOnScreen | None:
        if not is_rect(obj):
            return None

        w, h = self._tile_size
        cx, cy = coordinate
        map_coord = Coordinate(cx * w + obj.x, cy * h + obj.y)
        size = Size(obj.width, obj.height)
        return RectangleAreaOnScreen(map_coord, size)

    def _tile_layers(self, class_name: str) -> tuple[TiledTileLayer, ...]:
        return tuple(
            layer
            for layer in self._all_tile_layers
            if getattr(layer, "class", None) == class_name
            or class_name in layer.name
        )

    @cached_property
    def _all_tile_layers(self) -> tuple[TiledTileLayer, ...]:
        return tuple(self._layer(i) for i in self._tmx.visible_tile_layers)

    def _foreground(
        self, index: int, layer: TiledTileLayer
    ) -> ForegroundLayer | None:
        visited: set[_TileCoordinate] = set()
        groups: list[TileGroup] = []
        if not (drawings := self._drawing(layer)):
            return None
        for coordinate, resource in drawings.items():
            if coordinate in visited:
                continue
            connected: list[AnimationOnScreen | DrawingOnScreen] = []
            queue = deque([coordinate])
            visited.add(coordinate)
            while queue:
                curr = queue.popleft()
                connected.append(resource)
                for neighbor in self._neighbors(layer, curr):
                    if neighbor in drawings and neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            visible_bottom = max(
                resource.drawing_on_screen.visible_rectangle_area_on_screen.bottom
                for resource in connected
            )
            animation_on_screens = AnimationOnScreens(tuple(connected))
            tile_group = TileGroup(index, animation_on_screens, visible_bottom)
            groups.append(tile_group)
        tile_groups = tuple(sorted(groups))
        if layer.name == "foreground":
            breakpoint()
        return ForegroundLayer(index, tile_groups)

    @property
    def _tile_size(self) -> Size:
        return Size(self._tmx.tilewidth, self._tmx.tileheight)

    def _drawing(
        self, layer: TiledTileLayer
    ) -> dict[_TileCoordinate, AnimationOnScreen | DrawingOnScreen]:
        return {
            _TileCoordinate(top, left): self._tile(left, top, gid)
            for left, top, gid in layer
            if gid
        }

    def _tile(
        self, left: int, top: int, gid: _Gid
    ) -> AnimationOnScreen | DrawingOnScreen:
        width, height = self._tile_size
        coordinate = Coordinate(left * width, top * height)
        if frame_infos := self._tmx.tile_properties.get(gid, {}).get("frames"):
            frames = tuple(
                Drawing(self._tmx.images[frame_info.gid])
                for frame_info in frame_infos
            )
            durations = tuple(frame_info.duration for frame_info in frame_infos)
            animation = CyclicAnimation(frames, durations)
            return CyclicAnimationOnScreen(coordinate, animation)
        drawing = Drawing(self._tmx.images[gid])
        return DrawingOnScreen(coordinate, drawing)

    def _class(
        self, layer: TiledTileLayer, coordinate: _TileCoordinate
    ) -> str | None:
        x, y = coordinate
        if 0 <= x < len(layer.data) and 0 <= y < len(layer.data[x]):
            data_id = layer.data[x][y]
            return self._gid_to_cls.get(
                self._tmx.tile_properties.get(data_id, {}).get("id")
            )
        return None

    def _neighbors(
        self, layer: TiledTileLayer, coordinate: _TileCoordinate
    ) -> Iterable[_TileCoordinate]:
        x, y = coordinate
        if not (cls := self._class(layer, coordinate)):
            return
        for dx, dy in product((-1, 0, 1), repeat=2):
            neighbor = _TileCoordinate(x + dx, y + dy)
            if self._class(layer, neighbor) == cls:
                yield neighbor

    @cached_property
    def _gid_to_cls(self) -> dict[_Gid, str]:
        return {
            tile["id"]: cls
            for tile in self._tmx.tile_properties.values()
            if (cls := tile.get("type"))
        }

    @property
    def _init_collision_visuals(self) -> tuple[DrawingOnScreen, ...]:
        if config().debug and (
            color := config().debug.collision_rectangle_color
        ):
            return tuple(c.fill(color) for c in self.collisions)
        return ()

    @property
    def _init_foregrounds(self) -> ForegroundLayers:
        layers = tuple(
            layer
            for i, tile_layer in enumerate(
                self._tile_layers(config().map.foreground)
            )
            if (layer := self._foreground(i, tile_layer))
        )
        return ForegroundLayers(layers)

    def _draw_layers(self, class_name: str) -> AnimationOnScreens:
        resource = tuple(
            drawing
            for layer in self._tile_layers(class_name)
            for drawing in self._drawing(layer).values()
        )
        return AnimationOnScreens(resource)

    @property
    def _init_collisions(self) -> tuple[PolygonAreaOnScreen, ...]:
        from_tiles = tuple(
            self._polygon(coordinate, obj)
            for coordinate, obj in self._init_colliders
        )
        from_objects = tuple(
            poly
            for obj in self.get_objects_by_class_name(config().map.collision)
            if (poly := get_geometry(obj))
        )
        return from_tiles + from_objects


type _Gid = int


class _TileCoordinate(NamedTuple):
    top: int
    left: int


class _Collider(NamedTuple):
    coordinate: _TileCoordinate
    obj: TiledObject


def _below_character_layer(
    character: CharacterOnScreen, layer: ForegroundLayer
) -> bool:
    rect = character.drawing_on_screen.visible_rectangle_area_on_screen
    return any(
        tile_group.visible_bottom < rect.bottom
        and rect.collide(
            tile_group.tile.drawing_on_screen.visible_rectangle_area_on_screen
        )
        for tile_group in layer.tiles
    )
