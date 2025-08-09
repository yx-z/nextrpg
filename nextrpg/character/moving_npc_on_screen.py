from dataclasses import KW_ONLY, replace
from typing import Self, override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.moving_character_on_screen import MovingCharacterOnScreen
from nextrpg.character.npc_on_screen import NpcOnScreen, NpcSpec
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dataclass_with_init import (
    dataclass_with_init,
    default,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.core.walk import Walk
from nextrpg.draw.draw import PolygonOnScreen


@dataclass_with_init(frozen=True, kw_only=True)
class MovingNpcOnScreen(NpcOnScreen, MovingCharacterOnScreen):
    path: PolygonOnScreen
    spec: NpcSpec
    collisions: tuple[PolygonOnScreen, ...] = ()
    _: KW_ONLY = not_constructor_below()
    _walk: Walk = default(
        lambda self: Walk(
            self.path,
            self.spec.config.move_speed,
            self.spec.cyclic_walk and self.path.closed,
        )
    )

    @override
    def post_tick(self, time_delta: Millisecond, ticked: Self) -> Self:
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

    @override
    def can_move(
        self, coordinate: Coordinate, others: tuple[CharacterOnScreen, ...]
    ) -> bool:
        if self.spec.collide_with_others:
            return super().can_move(coordinate, others)
        return True
