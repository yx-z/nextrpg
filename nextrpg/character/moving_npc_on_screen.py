from __future__ import annotations

from dataclasses import KW_ONLY, replace
from typing import Self, override

from nextrpg.character.moving_character_on_screen import MovingCharacterOnScreen
from nextrpg.character.npc_on_screen import NpcOnScreen
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dataclass_with_init import (
    dataclass_with_init,
    default,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.core.walk import Walk
from nextrpg.draw.polyline_on_screen import PolylineOnScreen


@dataclass_with_init(frozen=True, kw_only=True)
class MovingNpcOnScreen(NpcOnScreen, MovingCharacterOnScreen):
    path: PolylineOnScreen
    _: KW_ONLY = not_constructor_below()
    # `coordinate` is initialized in the base class.
    # Hence, invoke `_walk` (given it's still an `_Init`) to initialize.
    coordinate: Coordinate = default(lambda self: self._walk(self).coordinate)
    _walk: Walk = default(lambda self: self._init_walk)

    @override
    def tick_after_character_and_coordinate(
        self, time_delta: Millisecond, ticked: Self
    ) -> Self:
        walk = self._walk.tick(time_delta)
        return replace(
            ticked, character=ticked.character.turn(walk.direction), _walk=walk
        )

    @property
    @override
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
