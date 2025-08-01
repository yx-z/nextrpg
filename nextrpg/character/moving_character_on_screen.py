from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, dataclass, replace
from typing import Self, override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dataclass_with_instance_init import not_constructor_below
from nextrpg.core.dimension import Size
from nextrpg.core.logger import Logger
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw import DrawOnScreen, PolygonOnScreen, RectangleOnScreen
from nextrpg.global_config.global_config import config

logger = Logger("MovingCharacterOnScreen")


@dataclass(frozen=True)
class MovingCharacterOnScreen(CharacterOnScreen, ABC):
    collisions: tuple[PolygonOnScreen, ...] = ()
    _: KW_ONLY = not_constructor_below()
    _move_toggle: bool = True

    @property
    def start_move(self) -> Self:
        return replace(self, _move_toggle=True)

    @property
    def stop_move(self) -> Self:
        return replace(self, _move_toggle=False)

    @property
    @abstractmethod
    def moving(self) -> bool: ...

    @abstractmethod
    def move(self, time_delta: Millisecond) -> Coordinate: ...

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        if not self.moving:
            return super().tick(time_delta)

        moved_coord = self.move(time_delta)
        character = (
            self.character.tick_move(time_delta)
            if self.moving
            else self.character.tick_idle(time_delta)
        )
        coordinate = (
            moved_coord
            if moved_coord and self._can_move(moved_coord)
            else self.coordinate
        )
        return replace(self, character=character, coordinate=coordinate)

    def _can_move(self, coordinate: Coordinate) -> bool:
        if (debug := config().debug) and debug.ignore_map_collisions:
            return True

        if collision := self._collide(self._collision_rectangle(coordinate)):
            logger.debug(t"Collided {collision.points}")
            return False
        return True

    def _collide(self, bounding_rect: RectangleOnScreen) -> PolygonOnScreen | None:
        for collision in self.collisions:
            if collision.collide(bounding_rect):
                return collision
        return None

