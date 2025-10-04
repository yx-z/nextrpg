from collections.abc import Iterable
from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from typing import Self

from pytmx import TiledObject, TiledTileLayer

from nextrpg.animation.animation_on_screen import AnimationOnScreen
from nextrpg.animation.animation_on_screens import AnimationOnScreens
from nextrpg.animation.cyclic_animation import CyclicAnimation
from nextrpg.animation.cyclic_animation_on_screen import CyclicAnimationOnScreen
from nextrpg.character.character_on_screen import CharacterOnScreen
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
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.geometry.polygon_area_on_screen import PolygonAreaOnScreen
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen

log = Log()


@dataclass(frozen=True)
class ForegroundLayers:
    tiles: tuple[AnimationOnScreens, ...]

    def tick(self, time_delta: Millisecond) -> Self:
        tiles = tuple(tile.tick(time_delta) for tile in self.tiles)
        return replace(self, tiles=tiles)

    def drawing_on_screens(
        self, characters: tuple[CharacterOnScreen, ...]
    ) -> tuple[DrawingOnScreen, ...]:
        character_drawing_on_screens = tuple(
            DrawingOnScreens(character.drawing_on_screens)
            for character in characters
        )
        tile_drawing_on_screens = tuple(
            DrawingOnScreens(tile.drawing_on_screens) for tile in self.tiles
        )
        all_drawing_on_screens = sorted(
            character_drawing_on_screens + tile_drawing_on_screens,
            key=lambda d: d.visible_rectangle_area_on_screen.bottom,
        )
        return tuple(
            drawing_on_screen
            for drawing_on_screens in all_drawing_on_screens
            for drawing_on_screen in drawing_on_screens.drawing_on_screens
        )


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
    collisions: tuple[AreaOnScreen, ...] = default(
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

    def _foreground(
        self, layer: TiledTileLayer
    ) -> tuple[AnimationOnScreens, ...]:

        def tile_class(coord: _TileCoordinate) -> str | None:
            if 0 <= coord.top < len(layer.data) and 0 <= coord.left < len(
                layer.data[coord.top]
            ):
                data_id = layer.data[coord.top][coord.left]
                return self._tmx.tile_properties.get(data_id, {}).get("type")
            return None

        visited: set[_TileCoordinate] = set()

        def neighbors(coord: _TileCoordinate) -> Iterable[_TileCoordinate]:
            if not (cls := tile_class(coord)):
                return
            for left_shift, top_shift in ((-1, 0), (0, -1), (1, 0), (0, 1)):
                left = coord.left + left_shift
                top = coord.top + top_shift
                neighbor = _TileCoordinate(left, top)
                if neighbor not in visited and tile_class(neighbor) == cls:
                    yield neighbor

        def dfs(coord: _TileCoordinate) -> list[_TileCoordinate]:
            connected = [coord]
            visited.add(coord)
            for neighbor in neighbors(coord):
                connected += dfs(neighbor)
            return connected

        groups: list[AnimationOnScreens] = []
        for coordinate in (drawings := self._drawing(layer)):
            if coordinate in visited:
                continue
            resources = tuple(
                drawings[coordinate] for coordinate in dfs(coordinate)
            )
            group = AnimationOnScreens(resources)
            groups.append(group)
        return tuple(groups)

    @property
    def _tile_size(self) -> Size:
        return Size(self._tmx.tilewidth, self._tmx.tileheight)

    def _drawing(
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
                Drawing(self._tmx.images[frame_info.gid])
                for frame_info in frame_infos
            )
            durations = tuple(frame_info.duration for frame_info in frame_infos)
            animation = CyclicAnimation(frames, durations)
            return CyclicAnimationOnScreen(coordinate, animation)
        drawing = Drawing(self._tmx.images[gid])
        return DrawingOnScreen(coordinate, drawing)

    @property
    def _init_collision_visuals(self) -> tuple[DrawingOnScreen, ...]:
        if config().debug and (
            color := config().debug.collision_rectangle_color
        ):
            return tuple(c.fill(color) for c in self.collisions)
        return ()

    @property
    def _init_foregrounds(self) -> ForegroundLayers:
        layers = self._tile_layers(config().map.foreground)
        tiles = tuple(
            tile for layer in layers for tile in self._foreground(layer)
        )
        return ForegroundLayers(tiles)

    def _draw_layers(self, class_name: str) -> AnimationOnScreens:
        resource = tuple(
            drawing
            for layer in self._tile_layers(class_name)
            for drawing in self._drawing(layer).values()
        )
        return AnimationOnScreens(resource)

    @property
    def _init_collisions(self) -> tuple[AreaOnScreen, ...]:
        from_tiles = tuple(
            self._polygon(collider) for collider in self._colliders
        )
        collision = config().map.collision
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
