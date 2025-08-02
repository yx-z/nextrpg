from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import Self, override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.logger import Logger
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw import PolygonOnScreen, RectangleOnScreen
from nextrpg.global_config.global_config import config

logger = Logger("MovingCharacterOnScreen")


@dataclass(frozen=True)
class MovingCharacterOnScreen(CharacterOnScreen, ABC):
    collisions: tuple[PolygonOnScreen, ...] = ()

    @property
    @abstractmethod
    def moving(self) -> bool: ...

    @abstractmethod
    def move(self, time_delta: Millisecond) -> Coordinate: ...

    @override
    def tick(
        self, time_delta: Millisecond, others: tuple[CharacterOnScreen, ...]
    ) -> Self:
        if not self.moving or (
            not self._can_move(moved_coord := self.move(time_delta), others)
        ):
            return super().tick(time_delta, others)

        character = (
            self.character.tick_move(time_delta)
            if self.moving
            else self.character.tick_idle(time_delta)
        )
        ticked = replace(self, character=character, coordinate=moved_coord)
        return self.post_tick(time_delta, ticked)

    def post_tick(self, time_delta: Millisecond, ticked: Self) -> Self:
        return ticked

    def _can_move(
        self, coordinate: Coordinate, others: tuple[CharacterOnScreen, ...]
    ) -> bool:
        if (debug := config().debug) and debug.ignore_map_collisions:
            return True

        if collision := self._collide(
            self._collision_rectangle(coordinate), others
        ):
            logger.debug(t"Collided {collision.points}")
            return False
        return True

    def _collide(
        self,
        bounding_rect: RectangleOnScreen,
        others: tuple[CharacterOnScreen, ...],
    ) -> PolygonOnScreen | None:
        other_rects = tuple(c.collision_rectangle for c in others)
        for collision in self.collisions + other_rects:
            if collision.collide(bounding_rect):
                return collision
        return None
