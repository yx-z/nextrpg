from __future__ import annotations

from dataclasses import KW_ONLY, replace
from functools import cached_property
from pathlib import Path
from typing import Self, override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_spec import CharacterSpec
from nextrpg.character.moving_npc_on_screen import MovingNpcOnScreen
from nextrpg.character.npc_on_screen import NpcOnScreen
from nextrpg.character.npc_spec import NpcSpec, to_strict
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.character.polygon_character_drawing import PolygonCharacterDrawing
from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.log import Log
from nextrpg.core.save import UpdateFromSave, concat_save_key
from nextrpg.core.time import Millisecond
from nextrpg.core.tmx_loader import get_geometry
from nextrpg.drawing.color import TRANSPARENT
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.polygon_drawing import PolygonDrawing
from nextrpg.drawing.rectangle_drawing import RectangleDrawing
from nextrpg.geometry.anchored_coordinate import BottomCenterCoordinate
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.polyline_on_screen import PolylineOnScreen
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.scene.map.map_loader import MapLoader
from nextrpg.scene.map.map_move import MapMove
from nextrpg.scene.map.map_shift import center_player
from nextrpg.scene.rpg_event.eventful_scene import EventfulScene
from nextrpg.scene.scene import Scene

log = Log()


@dataclass_with_default(frozen=True, kw_only=True)
class MapScene(EventfulScene, UpdateFromSave):
    tmx_file: Path
    player_spec: CharacterSpec
    move: MapMove | tuple[MapMove, ...] = ()
    npc_specs: NpcSpec | tuple[NpcSpec, ...] = ()
    _: KW_ONLY = private_init_below()
    _map_loader_input: MapLoader = default(
        lambda self: MapLoader(self.tmx_file)
    )
    npcs: tuple[NpcOnScreen, ...] = default(
        lambda self: tuple(self._init_npc(n) for n in self._npc_specs)
    )
    player: PlayerOnScreen = default(
        lambda self: self.init_player(self.player_spec)
    )
    _debug_visuals: tuple[DrawingOnScreen, ...] = default(
        lambda self: self._map_loader.collision_visuals
        + self._npc_paths
        + self._move_visuals
    )

    def init_player(self, player_spec: CharacterSpec) -> PlayerOnScreen:
        log.debug(t"Spawn player at {player_spec.unique_name}.")
        player_object = self._map_loader.get_object(player_spec.unique_name)
        bottom_center = BottomCenterCoordinate(player_object.x, player_object.y)
        top_left = bottom_center.anchor(player_spec.character.drawing).top_left
        map_collisions = self._map_loader.collisions
        return PlayerOnScreen(
            player_spec, top_left, map_collisions=map_collisions
        )

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        if move_to := self._move_to_scene(time_delta):
            return move_to
        if not isinstance(ticked := super().tick(time_delta), MapScene):
            return ticked
        map_loader = self._map_loader.tick(time_delta)
        return replace(ticked, _map_loader_input=map_loader)

    @cached_property
    @override
    def drawing_on_screens_shift(self) -> Coordinate:
        player_coord = self.player.center
        shift = center_player(player_coord, self._map_loader.map_size)
        log.debug(
            t"Player center coordinate {player_coord}. Shift {shift}",
            duration=100,
        )
        return shift

    @cached_property
    @override
    def drawing_on_screens_before_shift(self) -> tuple[DrawingOnScreen, ...]:
        foreground_and_characters = (
            self._map_loader.foregrounds.drawing_on_screens(
                self.player, self.npcs
            )
        )
        return (
            self._map_loader.background.drawing_on_screens
            + foreground_and_characters
            + self._map_loader.above_character.drawing_on_screens
            + self._debug_visuals
        )

    @override
    @cached_property
    def save_key(self) -> str:
        return concat_save_key(super().save_key, self.tmx_file)

    @override
    @property
    def save_data(self) -> dict:
        return {
            character.save_key: character.save_data
            for character in self.npcs + (self.player,)
        }

    @override
    def update_from_save(self, data: dict) -> Self:
        player = self.player.update_from_save(data[self.player.save_key])
        npcs = tuple(
            npc.update_from_save(data[npc.save_key]) for npc in self.npcs
        )
        return replace(self, player=player, npcs=npcs)

    @cached_property
    def _map_loader(self) -> MapLoader:
        if callable(self._map_loader_input):
            return self._map_loader_input(self)
        return self._map_loader_input

    def _move_to_scene(self, time_delta: Millisecond) -> Scene | None:
        for move in self._moves:
            if to_scene := self._move(move, time_delta):
                return to_scene
        return None

    @cached_property
    def _moves(self) -> tuple[MapMove, ...]:
        if isinstance(self.move, tuple):
            return self.move
        return (self.move,)

    @cached_property
    def _move_visuals(self) -> tuple[DrawingOnScreen, ...]:
        if config().debug and (color := config().debug.move_object_color):
            return tuple(m.fill(color) for m in self._move_areas)
        return ()

    @cached_property
    def _move_areas(self) -> tuple[AreaOnScreen, ...]:
        return tuple(
            get_geometry(self._map_loader.get_object(m.from_object))
            for m in self._moves
        )

    def _move(self, move: MapMove, time_delta: Millisecond) -> Scene | None:
        move_area = get_geometry(self._map_loader.get_object(move.from_object))
        assert isinstance(
            move_area, AreaOnScreen
        ), f"'{move.from_object}' needs to be an area."

        if self.player.drawing_on_screen.rectangle_area_on_screen.collide(
            move_area
        ):
            return move.move_to_scene(self, self.player).tick(time_delta)
        return None

    @cached_property
    def _npc_paths(self) -> tuple[DrawingOnScreen, ...]:
        if not (debug := config().debug) or not (color := debug.npc_path_color):
            return ()
        res: list[DrawingOnScreen] = []
        for npc in self.npcs:
            if not isinstance(npc, MovingNpcOnScreen):
                continue
            points = tuple(
                point.anchor(npc).bottom_center for point in npc.path.points
            )
            path = PolylineOnScreen(points).fill(color)
            res.append(path)
        return tuple(res)

    def _init_npc(self, spec: NpcSpec) -> NpcOnScreen:
        npc_object = self._map_loader.get_object(spec.unique_name)
        if not (poly := get_geometry(npc_object)):
            coordinate = BottomCenterCoordinate(npc_object.x, npc_object.y)
            return _init_standing_npc(spec, coordinate)

        if isinstance(spec.character, CharacterDrawing):
            return _init_moving_npc(spec, poly)
        # AreaOnScreen without CharacterDrawing -> static area triggering events
        return _init_area_npc(spec, poly)

    @cached_property
    def _npc_specs(self) -> tuple[NpcSpec, ...]:
        if isinstance(self.npc_specs, NpcSpec):
            return (self.npc_specs,)
        return self.npc_specs


def _init_standing_npc(
    spec: NpcSpec, bottom_center: BottomCenterCoordinate
) -> NpcOnScreen:
    assert isinstance(
        spec.character, CharacterDrawing
    ), f"Require CharacterDrawing for coordinate-only NPC {spec.unique_name}."
    coordinate = bottom_center.anchor(spec.character).top_left
    strict_spec = to_strict(spec)
    return NpcOnScreen(coordinate=coordinate, spec=strict_spec)


def _init_moving_npc(spec: NpcSpec, poly: AreaOnScreen) -> MovingNpcOnScreen:
    points = [
        p.as_bottom_center_of(spec.character).top_left for p in poly.points
    ]
    if isinstance(poly, AreaOnScreen):
        points.append(points[0])
    path = PolylineOnScreen(tuple(points))
    return MovingNpcOnScreen(path=path, spec=to_strict(spec))


def _init_area_npc(spec: NpcSpec, poly: AreaOnScreen) -> NpcOnScreen:
    coordinate = poly.top_left
    color = spec.character or TRANSPARENT
    if isinstance(poly, RectangleAreaOnScreen):
        drawing = RectangleDrawing(poly.size, color)
    else:
        points = tuple(p - coordinate for p in poly.points)
        drawing = PolygonDrawing(points, color)
    character_draw = PolygonCharacterDrawing(rect_or_poly=drawing)
    strict_spec = to_strict(spec, character_draw)
    return NpcOnScreen(coordinate=coordinate, spec=strict_spec)
