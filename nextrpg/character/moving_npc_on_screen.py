from dataclasses import KW_ONLY, replace
from functools import cached_property
from typing import Self, override

from nextrpg.character.moving_character_on_screen import MovingCharacterOnScreen
from nextrpg.character.npc_on_screen import NpcOnScreen
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.polyline_on_screen import PolylineOnScreen
from nextrpg.geometry.walk import Walk


@dataclass_with_default(frozen=True, kw_only=True)
class MovingNpcOnScreen(NpcOnScreen, MovingCharacterOnScreen):
    path: PolylineOnScreen
    _: KW_ONLY = private_init_below()
    map_collisions: tuple[AreaOnScreen] = ()
    coordinate: Coordinate = default(lambda self: self._walk.coordinate)
    map_collisions: tuple[AreaOnScreen, ...]
    _walk: Walk = default(lambda self: self._init_walk)

    @override
    def _tick_after_character_and_coordinate(
        self, time_delta: Millisecond, ticked: Self
    ) -> Self:
        walk = self._walk.tick(time_delta)
        return replace(
            ticked, character=ticked.character.turn(walk.direction), _walk=walk
        )

    @override
    @cached_property
    def moving(self) -> bool:
        return not self._event_started and not self._walk.complete

    @override
    def move(self, time_delta: Millisecond) -> Coordinate:
        return self._walk.tick(time_delta).coordinate

    @property
    def _init_walk(self) -> Walk:
        if (
            self.path.points[0] == self.path.points[-1]
            or not self.spec.cyclic_walk
        ):
            return Walk(
                self.path, self.spec.config.move_speed, self.spec.cyclic_walk
            )

        points = self.path.points + tuple(reversed(self.path.points))
        path = PolylineOnScreen(points)
        return Walk(path, self.spec.config.move_speed, self.spec.cyclic_walk)
