"""
Map scene implementation for `nextrpg`.

This module provides the `MapScene` class that represents a game map loaded from
Tiled TMX files. It handles map rendering, character movement with collision
detection, NPC management, and scene transitions between different map areas.

Features:
    - TMX map loading and rendering
    - Player movement with collision detection
    - NPC management and positioning
    - Scene transition handling
    - Depth-sorted rendering
    - Debug visualization support
    - Map object interaction
"""

from dataclasses import KW_ONLY, dataclass, field, replace
from functools import cached_property
from os import PathLike
from typing import NamedTuple, OrderedDict, override
from collections.abc import Callable

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
from nextrpg.draw.draw import DrawOnScreen
from nextrpg.global_config.global_config import config
from nextrpg.scene.map.loader import MapLoader, get_polygon
from nextrpg.scene.map.shift import center_player
from nextrpg.scene.rpg_event_scene import EventfulScene
from nextrpg.scene.scene import Scene
from nextrpg.scene.transition_scene import TransitionScene

logger = Logger("MapScene")


@dataclass_with_instance_init(frozen=True)
class MapScene(EventfulScene):
    """
    A scene implementation that represents a game map loaded from Tiled TMX.

    This class provides a complete map scene implementation that handles
    loading and rendering TMX maps, managing player and NPC movement,
    collision detection, and scene transitions. It integrates with the
    map helper system for map data processing and rendering.

    The scene supports multiple layers of map elements (background,
    foreground, above-character), proper depth sorting, collision
    detection, and debug visualization features.

    Arguments:
        `tmx_file`: Path to the Tiled TMX file to load.

        `player_spec`: Character specification representing the player.

        `moves`: Tuple of move objects to trigger when the player enters
            a new map area.

        `npc_specs`: Tuple of NPC specifications for NPCs in the map.

        `debug_visuals`: Debug visualization elements. Defaults to
            internal debug visuals.

        `npcs`: Tuple of NPC instances in the scene. Initialized from
            NPC specifications.

        `player`: Player character instance. Initialized from player
            specification.

    Example:
        ```python
        from nextrpg.map_scene import MapScene
        from nextrpg.character_on_screen import CharacterSpec

        # Create a map scene
        map_scene = MapScene(
            tmx_file="maps/town.tmx",
            player_spec=CharacterSpec(
                object_name="player_spawn",
                character=player_character
            ),
            moves=(move_to_shop, move_to_house),
            npc_specs=(merchant_spec, guard_spec)
        )
        ```
    """

    tmx_file: PathLike | str
    player_spec: CharacterSpec
    moves: Move | tuple[Move, ...] = field(default_factory=tuple)
    npc_specs: tuple[NpcSpec, ...] = field(default_factory=tuple)
    _: KW_ONLY = not_constructor_below()
    npcs: tuple[NpcOnScreen, ...] = instance_init(
        lambda self: tuple(self._init_npc(n) for n in self.npc_specs)
    )
    player: PlayerOnScreen = instance_init(
        lambda self: self.init_player(self.player_spec)
    )
    _debug_visuals: tuple[DrawOnScreen, ...] = instance_init(
        lambda self: self.map_helper.collision_visuals + self._npc_paths
    )

    @property
    def map_helper(self) -> MapLoader:
        """
        Get the map helper for this scene.

        Creates and caches a MapLoader instance for loading
        and processing the TMX map data.

        Returns:
            `MapLoader`: The map helper for this scene.

        Example:
            ```python
            helper = map_scene.map_helper
            collisions = helper.collisions
            ```
        """
        return MapLoader(self.tmx_file)

    def init_player(self, player_spec: CharacterSpec) -> PlayerOnScreen:
        """
        Initialize the player character for this map.

        Creates a PlayerOnScreen instance positioned at the
        specified map object location with collision detection.

        Arguments:
            `player_spec`: The player character specification.

        Returns:
            `PlayerOnScreen`: The initialized player character.

        Example:
            ```python
            player = map_scene.init_player(player_spec)
            ```
        """
        logger.debug(t"Spawn player at {player_spec.object_name}.")
        player = self.map_helper.get_object(player_spec.object_name)
        return PlayerOnScreen(
            character=player_spec.character,
            coordinate=Coordinate(player.x, player.y),
            collisions=self.map_helper.collisions,
            spec=player_spec,
        )

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        return self._move_to_scene or super().tick(time_delta)

    @cached_property
    @override
    def draw_on_screen_shift(self) -> Coordinate:
        player_coord = self.player.draw_on_screen.rectangle_on_screen.center
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
        layer_bottom_draws = sorted(
            draw
            for character in characters
            for draw in self.map_helper.layer_bottom_and_draw(character)
        )
        foregrounds = [t for layer in self.map_helper.foreground for t in layer]
        layers = sorted(foregrounds + layer_bottom_draws, key=lambda x: x[:2])
        return tuple(draw for _, _, draw in layers)

    @cached_property
    def _move_to_scene(self) -> TransitionScene | None:
        moves = self.moves if isinstance(self.moves, tuple) else (self.moves,)
        for move in moves:
            if m := self._move(move):
                return m
        return None

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
    """
    Move event from the current scene to another.

    This class defines a transition trigger that moves the player
    from one map scene to another when the player collides with
    a specific trigger object.

    Arguments:
        `to_object`: Name of the object to move to in the target scene.

        `trigger_object`: Name of the object that triggers the move.

        `next_scene`: Callable to get the next scene.

    Example:
        ```python
        from nextrpg.map_scene import Move

        # Create a move trigger
        move_to_shop = Move(
            to_object="shop_entrance",
            trigger_object="shop_door",
            next_scene=lambda spec: MapScene(
                tmx_file="maps/shop.tmx",
                player_spec=spec
            )
        )
        ```
    """

    to_object: str
    trigger_object: str
    next_scene: (
        Callable[[CharacterSpec | None], MapScene]
        | Callable[[CharacterSpec], MapScene]
    )

    def to_scene(
        self, from_scene: MapScene, player: PlayerOnScreen
    ) -> TransitionScene:
        """
        Create a transition to another scene.

        Creates a transition scene that moves the player from
        the current scene to the target scene, handling scene
        caching and player positioning.

        Arguments:
            `from_scene`: The current scene.

            `player`: The player character.

        Returns:
            `TransitionScene`: The transition to the next scene.

        Example:
            ```python
            transition = move.to_scene(current_scene, player)
            ```
        """
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
