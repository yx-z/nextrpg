from dataclasses import field, replace
from functools import cached_property

from nextrpg.character.npc_on_screen import (
    MovingNpcOnScreen,
    NpcOnScreen,
    StaticNpcOnScreen,
)
from nextrpg.character.npc_spec import MovingNpcSpec, StaticNpcSpec
from nextrpg.core import Millisecond
from nextrpg.draw_on_screen import Coordinate
from nextrpg.model import instance_init, register_instance_init
from nextrpg.scene.map_helper import MapHelper, get_polygon


def _init_static_npcs(self: Npcs) -> list[StaticNpcOnScreen]:
    return list(map(self._init_static_npc, self.static_npc_specs))


def _init_moving_npcs(self: Npcs) -> list[MovingNpcOnScreen]:
    return list(map(self._init_moving_npc, self.moving_npc_specs))


@register_instance_init
class Npcs:
    map_helper: MapHelper
    static_npc_specs: list[StaticNpcSpec] = field(default_factory=list)
    moving_npc_specs: list[MovingNpcSpec] = field(default_factory=list)
    _static_npcs: list[StaticNpcOnScreen] = instance_init(_init_static_npcs)
    _moving_npcs: list[MovingNpcOnScreen] = instance_init(_init_moving_npcs)

    @cached_property
    def list(self) -> list[NpcOnScreen]:
        return self._static_npcs + self._moving_npcs

    def tick(self, time_delta: Millisecond) -> Npcs:
        return replace(
            self,
            _static_npcs=[n.tick(time_delta) for n in self._static_npcs],
            _moving_npcs=[n.tick(time_delta) for n in self._moving_npcs],
        )

    @cached_property
    def _collided_npc(self) -> NpcOnScreen | None:
        collided = (npc for npc in self._npcs if self._collide_with_player(npc))
        return next(collided, None)

    def _collide_with_player(self, npc: NpcOnScreen) -> bool:
        return npc.draw_on_screen.rectangle.collide(
            self._player.draw_on_screen.rectangle
        )

    def _init_static_npc(self, spec: StaticNpcSpec) -> StaticNpcOnScreen:
        obj = self.map_helper.get_object(spec.name)
        return StaticNpcOnScreen(
            spec.drawing, Coordinate(obj.x, obj.y), name=spec.name
        )

    def _init_moving_npc(self, spec: MovingNpcSpec) -> MovingNpcOnScreen:
        obj = self.map_helper.get_object(spec.name)
        return MovingNpcOnScreen(
            spec.drawing,
            Coordinate(obj.x, obj.y),
            self.map_helper.collisions if spec.observe_collisions else [],
            spec.move_speed,
            name=spec.name,
            path=get_polygon(obj),
            idle_duration=spec.idle_duration,
            move_duration=spec.move_duration,
        )
