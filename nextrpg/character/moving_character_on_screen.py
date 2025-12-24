from abc import ABC, abstractmethod
from collections.abc import Collection, Iterable
from dataclasses import dataclass, replace
from typing import Self, override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.core.logger import Logger
from nextrpg.core.time import Millisecond
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen

logger = Logger("character")


@dataclass(frozen=True, kw_only=True)
class MovingCharacterOnScreen(CharacterOnScreen, ABC):
    map_collisions: tuple[AreaOnScreen, ...]

    @property
    @abstractmethod
    def moving(self) -> bool: ...

    @abstractmethod
    def move(self, time_delta: Millisecond) -> Coordinate: ...

    @override
    def tick_with_others(
        self, time_delta: Millisecond, others: Collection[CharacterOnScreen]
    ) -> Self:
        if not self.moving or (
            not self.can_move(moved_coordinate := self.move(time_delta), others)
        ):
            return super().tick_with_others(time_delta, others)

        character_drawing = (
            self.character_drawing.tick(time_delta)
            if self.moving
            else self.character_drawing.tick_idle(time_delta)
        )
        ticked = replace(
            self,
            character_drawing=character_drawing,
            coordinate=moved_coordinate,
        )
        return self._tick_after_character_and_coordinate(time_delta, ticked)

    def can_move(
        self, coordinate: Coordinate, others: Iterable[CharacterOnScreen]
    ) -> bool:
        if not self.spec.collide_with_others:
            return True

        collision_rectangle = self._collision_rectangle_area_on_screen(
            coordinate
        )
        if collision := self._collide(collision_rectangle, others):
            logger.debug(t"Collided {collision.points}")
            return False
        return True

    def _tick_after_character_and_coordinate(
        self, time_delta: Millisecond, ticked: Self
    ) -> Self:
        return ticked

    def _collide(
        self,
        bounding_rect: RectangleAreaOnScreen,
        others: Iterable[CharacterOnScreen],
    ) -> AreaOnScreen | None:
        other_rectangle_area_on_screens = tuple(
            c.collision_rectangle_area_on_screen
            for c in others
            if c.spec.collide_with_others
        )
        for collision in self.map_collisions + other_rectangle_area_on_screens:
            if collision.collide(bounding_rect):
                return collision
        return None
