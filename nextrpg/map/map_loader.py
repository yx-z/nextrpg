import heapq
from collections.abc import Iterable
from dataclasses import KW_ONLY, dataclass, field, replace
from functools import cached_property
from typing import Self

from pytmx import TiledObject, TiledTileLayer

from nextrpg.animation.animation_on_screen import AnimationOnScreen
from nextrpg.animation.animation_on_screens import AnimationOnScreens
from nextrpg.animation.cyclic_animation import CyclicAnimation
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.config.config import config
from nextrpg.config.map_config import MapConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.metadata import METADATA_CACHE_KEY, Metadata
from nextrpg.core.time import Millisecond
from nextrpg.core.tmx_loader import TmxLoader, get_geometry, is_rect
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.drawing_on_screens import (
    DrawingOnScreens,
    drawing_on_screens,
)
from nextrpg.drawing.sprite import tick_all
from nextrpg.drawing.sprite_on_screen import (
    SpriteOnScreen,
)
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate, YAxis
from nextrpg.geometry.polygon_area_on_screen import PolygonAreaOnScreen
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.geometry.size import Size


@dataclass(frozen=True)
class ForegroundLayers:
    tiles: tuple[AnimationOnScreens, ...]

    def tick(self, time_delta: Millisecond) -> Self:
        tiles = tick_all(self.tiles, time_delta)
        return replace(self, tiles=tiles)

    def drawing_on_screens(
        self, characters: Iterable[CharacterOnScreen]
    ) -> DrawingOnScreens:
        character_drawing_on_screens = sorted(
            (character.drawing_on_screens for character in characters),
            key=_sort_by_bottom,
        )
        tile_drawing_on_screens = [
            tile.drawing_on_screens for tile in self.tiles
        ]
        all_drawing_on_screens = heapq.merge(
            tile_drawing_on_screens,
            character_drawing_on_screens,
            key=_sort_by_bottom,
        )
        return drawing_on_screens(all_drawing_on_screens)


@dataclass_with_default(frozen=True)
class MapLoader(TmxLoader):
    config: MapConfig = field(default_factory=lambda: config().map)
    _: KW_ONLY = private_init_below()
    backgrounds: AnimationOnScreens = default(
        lambda self: self._draw_layers(self.config.background)
    )
    foregrounds: ForegroundLayers = default(lambda self: self._init_foregrounds)
    above_characters: AnimationOnScreens = default(
        lambda self: self._draw_layers(self.config.above_character)
    )
    collisions: tuple[AreaOnScreen, ...] = default(
        lambda self: self._init_collisions
    )

    def tick(self, time_delta: Millisecond) -> Self:
        backgrounds = self.backgrounds.tick(time_delta)
        foregrounds = self.foregrounds.tick(time_delta)
        above_characters = self.above_characters.tick(time_delta)
        return replace(
            self,
            backgrounds=backgrounds,
            foregrounds=foregrounds,
            above_characters=above_characters,
        )

    @cached_property
    def map_size(self) -> Size:
        width = self._tmx.width * self._tile_size.width
        height = self._tmx.height * self._tile_size.height
        return width * height

    @cached_property
    def _colliders(self) -> tuple[_Collider, ...]:
        return tuple(
            _Collider(_TileCoordinate(left, top), collider)
            for layer in self._all_tile_layers
            for top, left, gid in layer
            for collider in self._collider(gid)
        )

    def _collider(self, gid: _Gid) -> tuple[TiledObject, ...]:
        return tuple(
            self._tmx.tile_properties.get(gid, {}).get("colliders", ())
        )

    def _polygon(self, collider: _Collider) -> AreaOnScreen:
        return self._from_rect(collider) or self._from_points(collider)

    def _from_points(self, collider: _Collider) -> PolygonAreaOnScreen:
        width, height = self._tile_size
        left_shift = collider.coordinate.left * width
        top_shift = collider.coordinate.top * height
        points = tuple(
            Coordinate(left + left_shift, top + top_shift)
            for left, top in collider.object.as_points
        )
        return PolygonAreaOnScreen(points)

    def _from_rect(self, collider: _Collider) -> RectangleAreaOnScreen | None:
        if not is_rect(collider.object):
            return None

        width, height = self._tile_size
        left = collider.object.x + collider.coordinate.left * width
        top = collider.object.y + collider.coordinate.top * height
        map_coord = Coordinate(left, top)
        size = Size(collider.object.width, collider.object.height)
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

    def _tile_class(
        self, layer: TiledTileLayer, coordinate: _TileCoordinate
    ) -> str | None:
        tile_id = _tile_id(layer, coordinate)
        return self._tmx.tile_properties.get(tile_id, {}).get("type")

    def _connected(
        self,
        layer: TiledTileLayer,
        coordinate: _TileCoordinate,
        connected_tile_ids: set[_Gid] | None = None,
    ) -> set[_TileCoordinate]:
        res = {coordinate}
        if not (cls := self._tile_class(layer, coordinate)):
            return res

        coord_tile_id = _tile_id(layer, coordinate)
        if connected_tile_ids:
            connected_tile_ids.add(coord_tile_id)
        else:
            connected_tile_ids = {coord_tile_id}

        # Only need to search bottom and right, given the foreground traversal
        # (coordinate_to_resource) is already top-to-bottom and left-to-right.
        for left_shift, top_shift in ((1, 0), (0, 1)):
            neighbor = _TileCoordinate(
                coordinate.left + left_shift, coordinate.top + top_shift
            )
            if (
                self._tile_class(layer, neighbor) == cls
                and _tile_id(layer, neighbor) not in connected_tile_ids
            ):
                res |= self._connected(layer, neighbor, connected_tile_ids)
        return res

    def _foreground(
        self, layer: TiledTileLayer
    ) -> tuple[AnimationOnScreens, ...]:
        visited: set[_TileCoordinate] = set()
        groups: list[AnimationOnScreens] = []
        for coordinate in (resources := self._coordinate_to_resource(layer)):
            if coordinate in visited:
                continue
            connected_coordinates = self._connected(layer, coordinate)
            visited |= connected_coordinates
            connected_resources = tuple(
                resource
                for coordinate in connected_coordinates
                if (resource := resources.get(coordinate)) is not None
            )
            group = AnimationOnScreens(connected_resources)
            groups.append(group)
        return tuple(groups)

    @cached_property
    def _tile_size(self) -> Size:
        return Size(self._tmx.tilewidth, self._tmx.tileheight)

    def _coordinate_to_resource(
        self, layer: TiledTileLayer
    ) -> dict[_TileCoordinate, AnimationOnScreen | DrawingOnScreen]:
        return {
            _TileCoordinate(left, top): self._tile(left, top, gid)
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
                Drawing(
                    self._tmx.images[frame_info.gid],
                    metadata=self._metadata(frame_info.gid),
                )
                for frame_info in frame_infos
            )
            durations = tuple(frame_info.duration for frame_info in frame_infos)
            animation = CyclicAnimation(frames, durations)
            return animation.animation_on_screen(coordinate)
        drawing = Drawing(self._tmx.images[gid], metadata=self._metadata(gid))
        return drawing.drawing_on_screen(coordinate)

    def _metadata(self, gid: _Gid) -> Metadata:
        return METADATA_CACHE_KEY, ("tmx", self.file), ("gid", gid)

    @property
    def collision_visuals(self) -> DrawingOnScreens:
        if (debug := config().debug) and (color := debug.collision_rectangle):
            return drawing_on_screens(c.fill(color) for c in self.collisions)
        return DrawingOnScreens()

    @property
    def _init_foregrounds(self) -> ForegroundLayers:
        layers = self._tile_layers(self.config.foreground)
        tiles = sorted(
            (tile for layer in layers for tile in self._foreground(layer)),
            key=_sort_by_bottom,
        )
        return ForegroundLayers(tuple(tiles))

    def _draw_layers(self, class_name: str) -> AnimationOnScreens:
        resources = tuple(
            resource
            for layer in self._tile_layers(class_name)
            for resource in self._coordinate_to_resource(layer).values()
        )
        static = drawing_on_screens(
            resource
            for resource in resources
            if isinstance(resource, DrawingOnScreen)
        )
        dynamic = tuple(
            resource
            for resource in resources
            if not isinstance(resource, DrawingOnScreen)
        )
        if static:
            static_merged = static.drawing_on_screen
            merged = dynamic + (static_merged,)
        else:
            merged = dynamic
        return AnimationOnScreens(merged)

    @property
    def _init_collisions(self) -> tuple[AreaOnScreen, ...]:
        from_tiles = tuple(
            self._polygon(collider) for collider in self._colliders
        )
        collision = self.config.collision
        from_objects = tuple(
            poly
            for obj in self.get_objects_by_class_name(collision)
            if isinstance(poly := get_geometry(obj), AreaOnScreen)
        )
        from_layers = tuple(
            poly
            for index in self._tmx.visible_object_groups
            if getattr(layer := self._layer(index), "class", None) == collision
            or collision in layer.name
            for obj in layer
            if isinstance(poly := get_geometry(obj), AreaOnScreen)
        )
        return from_tiles + from_objects + from_layers


type _Gid = int


@dataclass(frozen=True)
class _TileCoordinate:
    left: int
    top: int


@dataclass(frozen=True)
class _Collider:
    coordinate: _TileCoordinate
    object: TiledObject


def _tile_id(layer: TiledTileLayer, coordinate: _TileCoordinate) -> _Gid:
    return layer.data[coordinate.top][coordinate.left]


def _sort_by_bottom(animation_on_screen_like: SpriteOnScreen) -> YAxis:
    return animation_on_screen_like.rectangle_area_on_screen.bottom
