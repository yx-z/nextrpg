from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, dataclass, field, replace
from typing import NamedTuple, Self, override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dataclass_with_instance_init import not_constructor_below
from nextrpg.core.dimension import PixelPerMillisecond
from nextrpg.core.direction import Direction
from nextrpg.core.logger import Logger
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw import DrawOnScreen, PolygonOnScreen
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

        rect = DrawOnScreen(coordinate, self.character.draw).rectangle_on_screen
        hit_coords = {
            Direction.LEFT: {rect.bottom_left, rect.center_left},
            Direction.RIGHT: {rect.bottom_right, rect.center_right},
            Direction.DOWN: {
                rect.bottom_right,
                rect.bottom_center,
                rect.bottom_left,
            },
            Direction.UP: {rect.center_right, rect.center, rect.center_left},
            Direction.UP_LEFT: {rect.center_left},
            Direction.UP_RIGHT: {rect.center_right},
            Direction.DOWN_LEFT: {
                rect.bottom_left,
                rect.center_left,
                rect.bottom_center,
            },
            Direction.DOWN_RIGHT: {
                rect.bottom_right,
                rect.center_right,
                rect.bottom_center,
            },
        }[self.character.direction]

        if collision_and_coord := self._collide(hit_coords):
            collision, coord = collision_and_coord
            logger.debug(t"Collision {coord} and {collision.points}")
            return False
        return True

    def _collide(
        self, hit_coords: set[Coordinate]
    ) -> _CollisionAndCoord | None:
        for collision in self.collisions:
            for coord in hit_coords:
                if coord in collision:
                    return _CollisionAndCoord(collision, coord)
        return None


class _CollisionAndCoord(NamedTuple):
    polygon: PolygonOnScreen
    coord: Coordinate
