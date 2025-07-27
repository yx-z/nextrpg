"""
Moving NPC implementation for `nextrpg`.

This module provides the implementation for non-player characters (NPCs) that can
move along paths in `nextrpg` games. It extends the moving character system with
NPC-specific pathing, idle/move timers, and walk cycles.

Features:
    - Path-based NPC movement
    - Idle and move state timers
    - Cyclic walk support
    - Integration with walk and timer systems
"""

from dataclasses import KW_ONLY, field, replace
from typing import Self, override

from nextrpg.character.moving_character_on_screen import MovingCharacterOnScreen
from nextrpg.character.npc_on_screen import NpcOnScreen, NpcSpec
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dataclass_with_instance_init import (
    dataclass_with_instance_init,
    instance_init,
    not_constructor_below,
)
from nextrpg.core.dimension import PixelPerMillisecond
from nextrpg.core.time import Millisecond, Timer
from nextrpg.core.walk import Walk
from nextrpg.draw.draw import PolygonOnScreen


@dataclass_with_instance_init(frozen=True, kw_only=True)
class MovingNpcOnScreen(NpcOnScreen, MovingCharacterOnScreen):
    """
    Moving NPC interface.

    Arguments:
        path: Polygon representing the path of the NPC.
    """

    path: PolygonOnScreen
    spec: NpcSpec
    collisions: tuple[PolygonOnScreen, ...] = field(default_factory=tuple)
    move_speed: PixelPerMillisecond = instance_init(
        lambda self: self.spec.move_speed
    )
    _: KW_ONLY = not_constructor_below()
    _walk: Walk = instance_init(
        lambda self: Walk(
            self.path,
            self.move_speed,
            self.spec.cyclic_walk and self.path.closed,
        )
    )

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        if not self.moving:
            return super().tick(time_delta)

        walk = self._walk.tick(time_delta)
        moved = MovingCharacterOnScreen.tick(self, time_delta)
        return replace(
            moved, character=moved.character.turn(walk.direction), _walk=walk
        )

    @property
    @override
    def moving(self) -> bool:
        return not self._event_triggered and not self._walk.complete

    @override
    def move(self, time_delta: Millisecond) -> Coordinate:
        return self._walk.tick(time_delta).coordinate
