from __future__ import annotations

from collections.abc import Callable
from dataclasses import KW_ONLY, dataclass, replace
from functools import cache, cached_property
from os import PathLike
from typing import override

from cachetools import LRUCache

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_on_screen import CharacterSpec
from nextrpg.character.moving_npc_on_screen import MovingNpcOnScreen
from nextrpg.character.npc_on_screen import NpcOnScreen
from nextrpg.character.npc_spec import NpcSpec, to_strict
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.character.polygon_character_drawing import PolygonCharacterDrawing
from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    not_constructor_below,
)
from nextrpg.core.log import Log
from nextrpg.core.time import Millisecond, get_timepoint
from nextrpg.draw.color import TRANSPARENT
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.draw.polygon_drawing import PolygonDrawing
from nextrpg.draw.rectangle_drawing import RectangleDrawing
from nextrpg.geometry.anchored_coordinate import BottomCenterCoordinate
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.polyline_on_screen import PolylineOnScreen
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.scene.map.map_loader import MapLoader, get_geometry
from nextrpg.scene.map.map_shift import center_player
from nextrpg.scene.rpg_event.eventful_scene import EventfulScene
from nextrpg.scene.scene import Scene
from nextrpg.scene.transition_scene import TransitionScene

log = Log()


@dataclass_with_default(frozen=True, kw_only=True)
class MapScene(EventfulScene):
    tmx_file: PathLike | str
    player_spec: CharacterSpec
    move: Move | tuple[Move, ...] = ()
    npc_specs: NpcSpec | tuple[NpcSpec, ...] = ()
    _: KW_ONLY = not_constructor_below()
    npcs: tuple[NpcOnScreen, ...] = default(
        lambda self: tuple(self._init_npc(n) for n in self._npc_specs)
    )
    player: PlayerOnScreen = default(
        lambda self: self.init_player(self.player_spec)
    )
    _debug_visuals: tuple[DrawingOnScreen, ...] = default(
        lambda self: self.map_helper.collision_visuals
        + self._npc_paths
        + self._move_visuals
    )

    @cached_property
    def map_helper(self) -> MapLoader:
        return MapLoader(self.tmx_file)

    def init_player(self, player_spec: CharacterSpec) -> PlayerOnScreen:
        log.debug(t"Spawn player at {player_spec.unique_name}.")
        player_object = self.map_helper.get_object(player_spec.unique_name)
        bottom_center = BottomCenterCoordinate(player_object.x, player_object.y)
        top_left = bottom_center.anchor(player_spec.character.drawing).top_left
        player = PlayerOnScreen(
            player_spec, top_left, map_collisions=self.map_helper.collisions
        )
        if self.save_io:
            return self.save_io.update(player)
        return player

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        return self._move_to_scene(time_delta) or super().tick(time_delta)

    @cached_property
    @override
    def drawing_on_screen_shift(self) -> Coordinate:
        player_coord = self.player.center
        shift = center_player(player_coord, self.map_helper.map_size)
        log.debug(
            t"Player center coordinate {player_coord}. Shift {shift}",
            duration=100,
        )
        return shift

    @cached_property
    @override
    def drawing_on_screens_before_shift(self) -> tuple[DrawingOnScreen, ...]:
        return (
            self.map_helper.background
            + self._foreground_and_characters
            + self.map_helper.above_character
            + self._debug_visuals
        )

    @cached_property
    def _foreground_and_characters(self) -> tuple[DrawingOnScreen, ...]:
        characters = (self.player,) + self.npcs
        layer_bottom_draws = tuple(
            drawing
            for character in characters
            for drawing in self.map_helper.layer_bottom_and_drawing(character)
        )
        foregrounds = tuple(
            tile for layer in self.map_helper.foreground for tile in layer
        )
        layers = sorted(foregrounds + layer_bottom_draws, key=lambda x: x[:2])
        return tuple(drawing_on_screen for _, _, drawing_on_screen in layers)

    def _move_to_scene(self, time_delta: Millisecond) -> Scene | None:
        for move in self._moves:
            if to_scene := self._move(move, time_delta):
                return to_scene
        return None

    @cached_property
    def _moves(self) -> tuple[Move, ...]:
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
            get_geometry(self.map_helper.get_object(m.trigger_object))
            for m in self._moves
        )

    def _move(self, move: Move, time_delta: Millisecond) -> Scene | None:
        move_area = get_geometry(
            self.map_helper.get_object(move.trigger_object)
        )
        assert isinstance(
            move_area, AreaOnScreen
        ), f"'{move.trigger_object}' needs to be an area."

        if self.player.drawing_on_screen.rectangle_area_on_screen.collide(
            move_area
        ):
            to_scene = move.to_scene(self, self.player)
            return to_scene.tick(time_delta)
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
        npc_object = self.map_helper.get_object(spec.unique_name)
        if not (poly := get_geometry(npc_object)):
            assert isinstance(
                spec.character, CharacterDrawing
            ), "Require CharacterDrawing for point-like NPC."
            bottom_center = BottomCenterCoordinate(npc_object.x, npc_object.y)
            coordinate = bottom_center.anchor(spec.character).top_left
            strict_spec = to_strict(spec)
            npc = NpcOnScreen(coordinate=coordinate, spec=strict_spec)
            return self._update_with_save(npc)

        if isinstance(spec.character, CharacterDrawing):
            points = [
                p.as_bottom_center_of(spec.character).top_left
                for p in poly.points
            ]
            if isinstance(poly, AreaOnScreen):
                points.append(points[0])
            path = PolylineOnScreen(tuple(points))
            npc = MovingNpcOnScreen(path=path, spec=to_strict(spec))
            return self._update_with_save(npc)

        # AreaOnScreen without CharacterDrawing -> static area triggering events
        coordinate = poly.top_left
        color = spec.character or TRANSPARENT
        if isinstance(poly, RectangleAreaOnScreen):
            drawing = RectangleDrawing(poly.size, color)
        else:
            points = tuple(p - coordinate for p in poly.points)
            drawing = PolygonDrawing(points, color)

        character_draw = PolygonCharacterDrawing(rect_or_poly=drawing)
        strict_spec = to_strict(spec, character_draw)
        npc = NpcOnScreen(coordinate=coordinate, spec=strict_spec)
        return self._update_with_save(npc)

    def _update_with_save(self, npc: NpcOnScreen) -> NpcOnScreen:
        if self.save_io:
            return self.save_io.update(npc)
        return npc

    @cached_property
    def _npc_specs(self) -> tuple[NpcSpec, ...]:
        if isinstance(self.npc_specs, NpcSpec):
            return (self.npc_specs,)
        return self.npc_specs


@dataclass(frozen=True)
class Move:
    to_object: str
    trigger_object: str
    next_scene: (
        Callable[[CharacterSpec | None], MapScene]
        | Callable[[CharacterSpec], MapScene]
    )

    def to_scene(
        self, from_scene: MapScene, player: PlayerOnScreen
    ) -> TransitionScene:
        spec = replace(
            player.spec, unique_name=self.to_object, character=player.character
        )
        now = get_timepoint()

        if not (tmx := _tmxs().get(self.next_scene)):
            next_scene = self.next_scene(spec)
            tmx = str(next_scene.tmx_file)

        if timed_scene := _scenes().get(tmx):
            scene = timed_scene.scene
            player = scene.init_player(spec)
            scene_with_player = replace(scene, player=player)

            time_delta = now - timed_scene.time
            to_scene = scene_with_player.tick(time_delta)
        else:
            to_scene = self.next_scene(spec)

        _scenes()[str(from_scene.tmx_file)] = _TimedScene(now, from_scene)
        _tmxs()[self.next_scene] = tmx

        return TransitionScene(from_scene=from_scene, to_scene=to_scene)


@dataclass(frozen=True)
class _TimedScene:
    time: Millisecond
    scene: MapScene


@cache
def _scenes() -> LRUCache[str, _TimedScene]:
    return LRUCache(config().map.cache_size)


@cache
def _tmxs() -> LRUCache[
    (
        Callable[[CharacterSpec | None], MapScene]
        | Callable[[CharacterSpec], MapScene]
    ),
    str,
]:
    return LRUCache(config().map.cache_size)
