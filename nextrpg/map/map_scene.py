import logging
from dataclasses import KW_ONLY, replace
from functools import cached_property
from itertools import chain
from typing import Self, override

from nextrpg.audio.music import play_music
from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.moving_npc_on_screen import MovingNpcOnScreen
from nextrpg.character.npc_on_screen import NpcOnScreen
from nextrpg.character.npc_spec import NpcSpec, to_strict_npc_spec
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.character.player_spec import PlayerSpec
from nextrpg.character.polygon_character_drawing import PolygonCharacterDrawing
from nextrpg.character.view_only_character_drawing import (
    ViewOnlyCharacterDrawing,
)
from nextrpg.config.config import config
from nextrpg.config.system.key_mapping_config import KeyMappingConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.logger import Logger
from nextrpg.core.time import Millisecond
from nextrpg.core.tmx_loader import get_geometry
from nextrpg.drawing.color import TRANSPARENT, Color
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.drawing_on_screens import (
    DrawingOnScreens,
    drawing_on_screens,
)
from nextrpg.drawing.polygon_drawing import PolygonDrawing
from nextrpg.drawing.rectangle_drawing import RectangleDrawing
from nextrpg.event.base_event import BaseEvent
from nextrpg.event.eventful_scene import EventfulScene
from nextrpg.event.io_event import is_key_press
from nextrpg.game.game_state import GameState
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.polyline_on_screen import PolylineOnScreen
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.map.map_loader import MapLoader
from nextrpg.map.map_move import MapMove
from nextrpg.map.map_shift import center_player
from nextrpg.map.map_spec import MapSpec
from nextrpg.scene.scene import Scene
from nextrpg.widget.menu_scene import MenuScene

on_screen_logger = Logger("map")
console_logger = logging.getLogger("map")


@dataclass_with_default(frozen=True, kw_only=True)
class MapScene(EventfulScene):
    spec: MapSpec
    _: KW_ONLY = private_init_below()
    map_loader: MapLoader = default(lambda self: MapLoader(self.spec.tmx))
    npcs: tuple[NpcOnScreen, ...] = default(
        lambda self: tuple(self._init_npc(n) for n in self._npc_specs)
    )
    player: PlayerOnScreen = default(
        lambda self: self.init_player(self.spec.player)
    )

    @cached_property
    def stop_player(self) -> Self:
        return replace(self, player=self.player.stop)

    def init_player(self, spec: PlayerSpec) -> PlayerOnScreen:
        on_screen_logger.debug(
            f"Spawn player at {spec.unique_name}.", console_logger
        )
        if not (coordinate := spec.coordinate_override):
            player_object = self.map_loader.get_object(spec.unique_name)
            coordinate = Coordinate(player_object.x, player_object.y)
        map_collisions = self.map_loader.collisions
        return PlayerOnScreen(
            spec=spec,
            coordinate=coordinate,
            map_collisions=map_collisions,
        )

    @override
    def tick(
        self, time_delta: Millisecond, state: GameState
    ) -> tuple[Scene, GameState]:
        play_music(self.spec.music)
        for move in self._moves:
            if res := self._move(move, time_delta, state):
                return res
        return super().tick(time_delta, state)

    @override
    def tick_without_event(
        self, time_delta: Millisecond, state: GameState
    ) -> tuple[Self, GameState]:
        ticked, state = super().tick_without_event(time_delta, state)
        map_loader = self.map_loader.tick(time_delta)
        tick_with_map_loader = replace(ticked, map_loader=map_loader)
        return tick_with_map_loader, state

    @override
    @cached_property
    def drawing_on_screens_shift(self) -> Coordinate:
        shift = center_player(self.player.center, self.map_loader.map_size)
        on_screen_logger.debug(
            f"Player center coordinate {self.player.center}. Shift {shift}",
            duration=None,
        )
        return shift

    @cached_property
    @override
    def drawing_on_screens_before_shift(self) -> DrawingOnScreens:
        player_tuple: tuple[CharacterOnScreen, ...] = (self.player,)
        characters = chain(player_tuple, self.npcs)
        foreground_and_characters = (
            self.map_loader.foregrounds.drawing_on_screens(characters)
        )
        return (
            self.map_loader.backgrounds.drawing_on_screens
            + foreground_and_characters
            + self.map_loader.above_characters.drawing_on_screens
            + self._debug_visuals
        )

    @override
    def event(
        self, event: BaseEvent, state: GameState
    ) -> tuple[Scene, GameState]:
        if (menu := config().menu) and is_key_press(
            event, KeyMappingConfig.cancel
        ):
            menu_scene = MenuScene(parent=self.stop_player, config=menu)
            return menu_scene, state
        return super().event(event, state)

    @cached_property
    def _debug_visuals(self) -> DrawingOnScreens:
        return (
            self.map_loader.collision_visuals
            + self._npc_paths
            + self._move_visuals
        )

    @cached_property
    def _moves(self) -> tuple[MapMove, ...]:
        if isinstance(self.spec.move, MapMove):
            return (self.spec.move,)
        return self.spec.move

    @cached_property
    def _move_visuals(self) -> DrawingOnScreens:
        if (debug := config().debug) and debug.move_object:
            return drawing_on_screens(
                m.fill(debug.move_object) for m in self._move_areas
            )
        return DrawingOnScreens()

    @cached_property
    def _move_areas(self) -> tuple[AreaOnScreen, ...]:
        return tuple(
            geometry
            for move in self._moves
            if isinstance(
                geometry := get_geometry(
                    self.map_loader.get_object(move.from_object)
                ),
                AreaOnScreen,
            )
        )

    def _move(
        self, move: MapMove, time_delta: Millisecond, state: GameState
    ) -> tuple[Scene, GameState] | None:
        move_object = self.map_loader.get_object(move.from_object)
        move_area = get_geometry(move_object)
        assert isinstance(
            move_area, AreaOnScreen
        ), f"'{move.from_object}' needs to be an area."

        if self.player.drawing_on_screen.rectangle_area_on_screen.collide(
            move_area
        ):
            moved, state = move(self, self.player, state)
            ticked, state = moved.tick(time_delta, state)
            return ticked, state
        return None

    @cached_property
    def _npc_paths(self) -> DrawingOnScreens:
        if not (debug := config().debug) or not (color := debug.npc_path):
            return DrawingOnScreens()
        res: list[DrawingOnScreen] = []
        for npc in self.npcs:
            if isinstance(npc, MovingNpcOnScreen):
                path = PolylineOnScreen(npc.path.points).fill(color)
                res.append(path)
        return drawing_on_screens(res)

    def _init_npc(self, spec: NpcSpec) -> NpcOnScreen:
        npc_object = self.map_loader.get_object(spec.unique_name)
        poly = get_geometry(npc_object)
        if (spec.character_drawing and not poly) or npc_object.image:
            if npc_object.image:
                # Tile as character drawing.
                drawing = Drawing(npc_object.image)
                character_drawing = ViewOnlyCharacterDrawing(resource=drawing)
                spec = replace(spec, character_drawing=character_drawing)

            coordinate = Coordinate(npc_object.x, npc_object.y)
            return _init_standing_npc(spec, coordinate)

        if isinstance(spec.character_drawing, CharacterDrawing):
            return _init_moving_npc(spec, poly)
        # AreaOnScreen without CharacterDrawing -> static area triggering events
        return _init_area_npc(spec, poly)

    @cached_property
    def _npc_specs(self) -> tuple[NpcSpec, ...]:
        if isinstance(self.spec.npc, NpcSpec):
            return (self.spec.npc,)
        return self.spec.npc


def _init_standing_npc(spec: NpcSpec, coordinate: Coordinate) -> NpcOnScreen:
    assert isinstance(
        spec.character_drawing, CharacterDrawing
    ), f"Require CharacterDrawing for coordinate-only NPC {spec.unique_name}."
    strict_spec = to_strict_npc_spec(spec)
    return NpcOnScreen(coordinate=coordinate, spec=strict_spec)


def _init_moving_npc(spec: NpcSpec, poly: AreaOnScreen) -> MovingNpcOnScreen:
    if isinstance(poly, AreaOnScreen):
        points = poly.points + (poly.points[0],)
    else:
        points = (poly.points,)
    path = PolylineOnScreen(points)
    strict_spec = to_strict_npc_spec(spec)
    return MovingNpcOnScreen(path=path, spec=strict_spec)


def _init_area_npc(spec: NpcSpec, poly: AreaOnScreen) -> NpcOnScreen:
    coordinate = poly.top_left
    color = spec.character_drawing or TRANSPARENT
    assert isinstance(
        color, Color
    ), f"Expect Color in NpcSpec. Got {spec.character_drawing}"
    if isinstance(poly, RectangleAreaOnScreen):
        drawing = RectangleDrawing(poly.size, color)
    else:
        points = tuple(p - coordinate for p in poly.points)
        drawing = PolygonDrawing(points, color)
    character_draw = PolygonCharacterDrawing(rect_or_poly=drawing)
    strict_spec = to_strict_npc_spec(spec, character_draw)
    return NpcOnScreen(
        coordinate=coordinate, spec=strict_spec, anchor=Anchor.TOP_LEFT
    )
