from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import Self, override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.log import Log
from nextrpg.core.time import Millisecond
from nextrpg.draw.polygon_on_screen import PolygonOnScreen
from nextrpg.draw.rectangle_on_screen import RectangleOnScreen

log = Log()


@dataclass(frozen=True)
class MovingCharacterOnScreen(CharacterOnScreen, ABC):
    map_collisions: tuple[PolygonOnScreen, ...] = ()

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
            not self.can_move(moved_coord := self.move(time_delta), others)
        ):
            return super().tick(time_delta, others)

        character = (
            self.character.tick_move(time_delta)
            if self.moving
            else self.character.tick_idle(time_delta)
        )
        ticked = replace(self, character=character, coordinate=moved_coord)
        return self.tick_after_character_and_coordinate(time_delta, ticked)

    def tick_after_character_and_coordinate(
        self, time_delta: Millisecond, ticked: Self
    ) -> Self:
        return ticked

    def can_move(
        self, coordinate: Coordinate, others: tuple[CharacterOnScreen, ...]
    ) -> bool:
        if not self.spec.collide_with_others:
            return True

        if collision := self._collide(
            self._collision_rectangle(coordinate), others
        ):
            log.debug(t"Collided {collision.points}")
            return False
        return True

    def _collide(
        self,
        bounding_rect: RectangleOnScreen,
        others: tuple[CharacterOnScreen, ...],
    ) -> PolygonOnScreen | None:
        other_rects = tuple(
            c.collision_rectangle for c in others if c.spec.collide_with_others
        )
        for collision in self.map_collisions + other_rects:
            if collision.collide(bounding_rect):
                return collision
        return None
