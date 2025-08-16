from __future__ import annotations

from collections.abc import Callable
from dataclasses import KW_ONLY, dataclass, replace
from functools import cache, cached_property
from os import PathLike
from typing import NamedTuple, override

from cachetools import LRUCache

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_on_screen import CharacterSpec
from nextrpg.character.moving_npc_on_screen import MovingNpcOnScreen
from nextrpg.character.npc_on_screen import NpcOnScreen, NpcSpec, to_strict
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.character.polygon_character_draw import PolygonCharacterDrawing
from nextrpg.core.color import TRANSPARENT
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dataclass_with_init import (
    dataclass_with_init,
    default,
    not_constructor_below,
)
from nextrpg.core.direction import Direction
from nextrpg.core.log import Log
from nextrpg.core.time import Millisecond, get_timepoint
from nextrpg.draw.drawing import (
    DrawingOnScreen,
    PolygonDrawing,
    PolygonOnScreen,
    RectangleDrawing,
    RectangleOnScreen,
)
from nextrpg.global_config.global_config import config
from nextrpg.scene.map.map_loader import MapLoader, get_polygon
from nextrpg.scene.map.map_shift import center_player
from nextrpg.scene.rpg_event.eventful_scene import EventfulScene
from nextrpg.scene.scene import Scene
from nextrpg.scene.transition_scene import TransitionScene

log = Log()


@dataclass_with_init(frozen=True, kw_only=True)
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

    @property
    def map_helper(self) -> MapLoader:
        return MapLoader(self.tmx_file)

    def init_player(self, player_spec: CharacterSpec) -> PlayerOnScreen:
        log.debug(t"Spawn player at {player_spec.unique_name}.")
        player = self.map_helper.get_object(player_spec.unique_name)
        player = PlayerOnScreen(
            player_spec,
            Coordinate(player.x, player.y),
            map_collisions=self.map_helper.collisions,
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
        layer_bottom_draws = list(
            drawing
            for character in characters
            for drawing in self.map_helper.layer_bottom_and_drawing(character)
        )
        foregrounds = [t for layer in self.map_helper.foreground for t in layer]
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
            return tuple(m.fill(color) for m in self._move_polys)
        return ()

    @cached_property
    def _move_polys(self) -> tuple[PolygonOnScreen, ...]:
        return tuple(
            get_polygon(self.map_helper.get_object(m.trigger_object))
            for m in self._moves
        )

    def _move(self, move: Move, time_delta: Millisecond) -> Scene | None:
        move_poly = get_polygon(self.map_helper.get_object(move.trigger_object))
        if self.player.drawing_on_screen.rectangle_on_screen.collide(move_poly):
            to_scene = move.to_scene(self, self.player)
            return to_scene.tick(time_delta)
        return None

    @cached_property
    def _npc_paths(self) -> tuple[DrawingOnScreen, ...]:
        if not (debug := config().debug) or not (color := debug.npc_path_color):
            return ()
        return tuple(
            npc.path.line(color)
            for npc in self.npcs
            if isinstance(npc, MovingNpcOnScreen)
        )

    def _init_npc(self, spec: NpcSpec) -> NpcOnScreen:
        obj = self.map_helper.get_object(spec.unique_name)
        coordinate = Coordinate(obj.x, obj.y)
        if not (poly := get_polygon(obj)):
            return NpcOnScreen(coordinate=coordinate, spec=to_strict(spec))

        if isinstance(spec.character, CharacterDrawing):
            npc = MovingNpcOnScreen(
                coordinate=coordinate, path=poly, spec=to_strict(spec)
            )
            if self.save_io:
                return self.save_io.update(npc)
            return npc

        color = spec.character or TRANSPARENT
        if isinstance(poly, RectangleOnScreen):
            poly_draw = RectangleDrawing(poly.size, color)
        else:
            points = tuple(p - coordinate for p in poly.points)
            poly_draw = PolygonDrawing(points, color)

        poly_spec = to_strict(
            spec, PolygonCharacterDrawing(Direction.DOWN, poly_draw)
        )
        npc = NpcOnScreen(coordinate=coordinate, spec=poly_spec)
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
            timepoint, scene = timed_scene
            time_delta = now - timepoint
            scene_with_player = replace(scene, player=scene.init_player(spec))
            to_scene = scene_with_player.tick(time_delta)
        else:
            to_scene = self.next_scene(spec)

        _scenes()[str(from_scene.tmx_file)] = _TimedScene(now, from_scene)
        _tmxs()[self.next_scene] = tmx

        return TransitionScene(from_scene=from_scene, to_scene=to_scene)


class _TimedScene(NamedTuple):
    time: Millisecond
    scene: MapScene


@cache
def _scenes() -> LRUCache[str, _TimedScene]:
    return LRUCache(config().map.cache_size)


@cache
def _tmxs() -> LRUCache[Callable, str]:
    return LRUCache(config().map.cache_size)
