from __future__ import annotations

from collections.abc import Callable
from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from os import PathLike
from typing import NamedTuple, OrderedDict, override

from nextrpg.character.character_on_screen import CharacterSpec
from nextrpg.character.moving_npc_on_screen import MovingNpcOnScreen
from nextrpg.character.npc_on_screen import NpcOnScreen, NpcSpec
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dataclass_with_instance_init import (
    dataclass_with_instance_init,
    instance_init,
    not_constructor_below,
)
from nextrpg.core.logger import Logger
from nextrpg.core.time import Millisecond, get_timepoint
from nextrpg.draw.draw import DrawOnScreen, PolygonOnScreen
from nextrpg.global_config.global_config import config
from nextrpg.scene.map.map_loader import MapLoader, get_polygon
from nextrpg.scene.map.map_shift import center_player
from nextrpg.scene.rpg_event.eventful_scene import EventfulScene
from nextrpg.scene.scene import Scene
from nextrpg.scene.transition_scene import TransitionScene

logger = Logger()


@dataclass_with_instance_init(frozen=True)
class MapScene(EventfulScene):
    tmx_file: PathLike | str
    player_spec: CharacterSpec
    move: Move | tuple[Move, ...] = ()
    npc_specs: tuple[NpcSpec, ...] = ()
    _: KW_ONLY = not_constructor_below()
    npcs: tuple[NpcOnScreen, ...] = instance_init(
        lambda self: tuple(self._init_npc(n) for n in self.npc_specs)
    )
    player: PlayerOnScreen = instance_init(
        lambda self: self.init_player(self.player_spec)
    )
    _debug_visuals: tuple[DrawOnScreen, ...] = instance_init(
        lambda self: self.map_helper.collision_visuals
        + self._npc_paths
        + self._move_visuals
    )

    @property
    def map_helper(self) -> MapLoader:
        return MapLoader(self.tmx_file)

    def init_player(self, player_spec: CharacterSpec) -> PlayerOnScreen:
        logger.debug(t"Spawn player at {player_spec.object_name}.")
        player = self.map_helper.get_object(player_spec.object_name)
        return PlayerOnScreen(
            player_spec,
            Coordinate(player.x, player.y),
            collisions=self.map_helper.collisions,
        )

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        return self._move_to_scene or super().tick(time_delta)

    @cached_property
    @override
    def draw_on_screen_shift(self) -> Coordinate:
        player_coord = self.player.center
        shift = center_player(player_coord, self.map_helper.map_size)
        logger.debug(
            t"Player center coord {player_coord}. Shift {shift}", duration=100
        )
        return shift

    @cached_property
    @override
    def draw_on_screens_before_shift(self) -> tuple[DrawOnScreen, ...]:
        return (
            self.map_helper.background
            + self._foreground_and_characters
            + self.map_helper.above_character
            + self._debug_visuals
        )

    @cached_property
    def _foreground_and_characters(self) -> tuple[DrawOnScreen, ...]:
        characters = (self.player,) + self.npcs
        layer_bottom_draws = list(
            draw
            for character in characters
            for draw in self.map_helper.layer_bottom_and_draw(character)
        )
        foregrounds = [t for layer in self.map_helper.foreground for t in layer]
        layers = sorted(foregrounds + layer_bottom_draws, key=lambda x: x[:2])
        return tuple(draw for _, _, draw in layers)

    @cached_property
    def _move_to_scene(self) -> TransitionScene | None:
        for move in self._moves:
            if m := self._move(move):
                return m
        return None

    @cached_property
    def _moves(self) -> tuple[Move, ...]:
        if isinstance(self.move, tuple):
            return self.move
        return (self.move,)

    @cached_property
    def _move_visuals(self) -> tuple[DrawOnScreen, ...]:
        if config().debug and (color := config().debug.move_object_color):
            return tuple(m.fill(color) for m in self._move_polys)
        return ()

    @cached_property
    def _move_polys(self) -> tuple[PolygonOnScreen, ...]:
        return tuple(
            get_polygon(self.map_helper.get_object(m.trigger_object))
            for m in self._moves
        )

    def _move(self, move: Move) -> TransitionScene | None:
        move_poly = get_polygon(self.map_helper.get_object(move.trigger_object))
        if self.player.draw_on_screen.rectangle_on_screen.collide(move_poly):
            return move.to_scene(self, self.player)
        return None

    @cached_property
    def _npc_paths(self) -> tuple[DrawOnScreen, ...]:
        if not (debug := config().debug) or not (color := debug.npc_path_color):
            return ()
        return tuple(
            npc.path.line(color)
            for npc in self.npcs
            if isinstance(npc, MovingNpcOnScreen)
        )

    def _init_npc(self, spec: NpcSpec) -> NpcOnScreen:
        obj = self.map_helper.get_object(spec.object_name)
        coord = Coordinate(obj.x, obj.y)
        if poly := get_polygon(obj):
            return MovingNpcOnScreen(coordinate=coord, path=poly, spec=spec)
        return NpcOnScreen(coordinate=coord, spec=spec)


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
            player.spec, object_name=self.to_object, character=player.character
        )
        now = get_timepoint()

        if not (tmx := _tmxs.get(self.next_scene)):
            next_scene = self.next_scene(spec)
            tmx = str(next_scene.tmx_file)

        if timed_scene := _scenes.get(tmx):
            timepoint, scene = timed_scene
            time_delta = now - timepoint
            scene_with_player = replace(scene, player=scene.init_player(spec))
            to_scene = scene_with_player.tick(time_delta)
        else:
            to_scene = self.next_scene(spec)

        while _scenes and len(_scenes) >= config().resource.map_cache_size:
            _scenes.popitem(last=False)
        _scenes[str(from_scene.tmx_file)] = _TimedScene(now, from_scene)

        while _tmxs and len(_tmxs) >= config().resource.map_cache_size:
            _tmxs.popitem(last=False)
        _tmxs[self.next_scene] = tmx

        return TransitionScene(from_scene=from_scene, to_scene=to_scene)


class _TimedScene(NamedTuple):
    time: Millisecond
    scene: MapScene


_scenes: OrderedDict[str, _TimedScene] = OrderedDict()
_tmxs: OrderedDict[Callable, str] = OrderedDict()
