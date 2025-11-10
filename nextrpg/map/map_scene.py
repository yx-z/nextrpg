import inspect
from collections.abc import Callable
from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from pathlib import Path
from typing import Any, Self, override

from nextrpg.character.character_drawing import CharacterDrawing
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
from nextrpg.core.log import Log
from nextrpg.core.module_and_attribute import (
    ModuleAndAttribute,
)
from nextrpg.core.save import UpdateFromSave
from nextrpg.core.time import Millisecond
from nextrpg.core.tmx_loader import get_geometry
from nextrpg.drawing.color import TRANSPARENT, Color
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.polygon_drawing import PolygonDrawing
from nextrpg.drawing.rectangle_drawing import RectangleDrawing
from nextrpg.event.eventful_scene import EventfulScene
from nextrpg.event.io_event import IoEvent, is_key_press
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.polyline_on_screen import PolylineOnScreen
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.map.map_loader import MapLoader
from nextrpg.map.map_move import MapMove
from nextrpg.map.map_shift import center_player
from nextrpg.scene.scene import Scene
from nextrpg.widget.menu_scene import MenuScene

log = Log()


def _infer_creation_function() -> ModuleAndAttribute[Callable]:
    frame = inspect.stack()[2]
    module = inspect.getmodule(frame[0]).__name__
    return ModuleAndAttribute(module, frame.function)


@dataclass_with_default(frozen=True, kw_only=True)
class MapScene(EventfulScene, UpdateFromSave[dict[str, Any]]):
    tmx: Path
    player_spec: PlayerSpec
    move: MapMove | tuple[MapMove, ...] = ()
    npc_specs: NpcSpec | tuple[NpcSpec, ...] = ()
    creation_function: ModuleAndAttribute = field(
        default_factory=_infer_creation_function
    )
    _: KW_ONLY = private_init_below()
    _map_loader_input: MapLoader | Callable[[MapScene], MapLoader] = default(
        lambda self: MapLoader(self.tmx)
    )
    npcs: tuple[NpcOnScreen, ...] = default(
        lambda self: tuple(self._init_npc(n) for n in self._npc_specs)
    )
    player: PlayerOnScreen = default(
        lambda self: self.init_player(self.player_spec)
    )

    @cached_property
    def _debug_visuals(self) -> list[DrawingOnScreen]:
        return (
            self._map_loader.collision_visuals
            + self._npc_paths
            + self._move_visuals
        )

    @cached_property
    def stop_player(self) -> Self:
        return replace(self, player=self.player.stop)

    def init_player(self, player_spec: PlayerSpec) -> PlayerOnScreen:
        log.debug(t"Spawn player at {player_spec.unique_name}.")
        if not (coordinate := player_spec.coordinate_override):
            player_object = self._map_loader.get_object(player_spec.unique_name)
            coordinate = Coordinate(player_object.x, player_object.y)
        map_collisions = self._map_loader.collisions
        return PlayerOnScreen(
            player_spec,
            coordinate,
            map_collisions=map_collisions,
        )

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        if move_to := self._move_to_scene(time_delta):
            return move_to
        return super().tick(time_delta)

    @override
    def tick_without_event(self, time_delta: Millisecond) -> Self:
        ticked = super().tick_without_event(time_delta)
        map_loader = self._map_loader.tick(time_delta)
        return replace(ticked, _map_loader_input=map_loader)

    @override
    @cached_property
    def drawing_on_screens_shift(self) -> Coordinate:
        player_coord = self.player.center
        shift = center_player(player_coord, self._map_loader.map_size)
        log.debug(
            t"Player center coordinate {player_coord}. Shift {shift}",
            duration=None,
        )
        return shift

    @cached_property
    @override
    def drawing_on_screens_before_shift(self) -> list[DrawingOnScreen]:
        characters = [self.player] + list(self.npcs)
        foreground_and_characters = (
            self._map_loader.foregrounds.drawing_on_screens(characters)
        )
        return (
            self._map_loader.backgrounds.drawing_on_screens
            + foreground_and_characters
            + self._map_loader.above_characters.drawing_on_screens
            + self._debug_visuals
        )

    @override
    def event(self, event: IoEvent) -> Scene:
        if (menu := config().menu) and is_key_press(
            event, KeyMappingConfig.cancel
        ):
            return MenuScene(map=self, widget=menu.widget, tmx=menu.tmx)
        return super().event(event)

    @override
    @cached_property
    def save_data(self) -> dict:
        return {
            character.name: character.save_data
            for character in (self.player,) + self.npcs
        }

    @override
    def update_from_save(self, data: dict[str, Any]) -> Self:
        player = self.player.update_from_save(data[self.player.name])
        npcs = tuple(npc.update_from_save(data[npc.name]) for npc in self.npcs)
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
    def _moves(self) -> list[MapMove]:
        if isinstance(self.move, MapMove):
            return [self.move]
        return list(self.move)

    @cached_property
    def _move_visuals(self) -> list[DrawingOnScreen]:
        if (debug := config().debug) and debug.move_object_color:
            return [m.fill(debug.move_object_color) for m in self._move_areas]
        return []

    @cached_property
    def _move_areas(self) -> list[AreaOnScreen]:
        return [
            geometry
            for move in self._moves
            if isinstance(
                geometry := get_geometry(
                    self._map_loader.get_object(move.from_object)
                ),
                AreaOnScreen,
            )
        ]

    def _move(self, move: MapMove, time_delta: Millisecond) -> Scene | None:
        move_object = self._map_loader.get_object(move.from_object)
        move_area = get_geometry(move_object)
        assert isinstance(
            move_area, AreaOnScreen
        ), f"'{move.from_object}' needs to be an area."

        if self.player.drawing_on_screen.rectangle_area_on_screen.collide(
            move_area
        ):
            return move.move_to_scene(self, self.player).tick(time_delta)
        return None

    @cached_property
    def _npc_paths(self) -> list[DrawingOnScreen]:
        if not (debug := config().debug) or not (color := debug.npc_path_color):
            return []
        res: list[DrawingOnScreen] = []
        for npc in self.npcs:
            if isinstance(npc, MovingNpcOnScreen):
                path = PolylineOnScreen(npc.path.points).fill(color)
                res.append(path)
        return res

    def _init_npc(self, spec: NpcSpec) -> NpcOnScreen:
        print(spec.unique_name)
        npc_object = self._map_loader.get_object(spec.unique_name)
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
    def _npc_specs(self) -> list[NpcSpec]:
        if isinstance(self.npc_specs, NpcSpec):
            return [self.npc_specs]
        return list(self.npc_specs)


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
    assert isinstance(
        color := spec.character_drawing or TRANSPARENT, Color
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
