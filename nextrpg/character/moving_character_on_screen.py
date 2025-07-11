from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import NamedTuple, Self, override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.config import config
from nextrpg.core import Direction, Millisecond, PixelPerMillisecond
from nextrpg.draw.coordinate import Coordinate
from nextrpg.draw.draw_on_screen import DrawOnScreen, Polygon
from nextrpg.logger import Logger

logger = Logger("MovingCharacterOnScreen")


@dataclass(kw_only=True, frozen=True)
class MovingCharacterOnScreen(CharacterOnScreen, ABC):
    collisions: tuple[Polygon, ...]
    move_speed: PixelPerMillisecond = field(
        default_factory=lambda: config().character.move_speed
    )

    @cached_property
    @abstractmethod
    def moving(self) -> bool:
        """
        Get whether the character is currently moving.

        Returns:
            `bool`: Whether the character is currently moving.
        """

    @abstractmethod
    def move(self, time_delta: Millisecond) -> Coordinate:
        """
        Move the character based on the current speed and time delta.

        Arguments:
            `time_delta`: The time that has passed since the last update.

        Returns:
            `Coordinate`: The updated character position after the move step.
        """

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        """
        Update the character's state for a single game step/frame.

        Calculates movement based on currently pressed keys, handles collision
        detection, and updates the character's drawing state (moving or idle).

        Arguments:
            `time_delta`: The time that has passed since
                the last update, used for calculating movement distance.

        Returns:
            `CharacterOnScreen`: The updated character state after the step.
        """
        if self._event_triggered:
            return super().tick(time_delta)

        moved_coord = self.move(time_delta) if self.moving else None
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

        rect = DrawOnScreen(coordinate, self.character.drawing).rectangle
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
                if collision.contain(coord):
                    return _CollisionAndCoord(collision, coord)
        return None


class _CollisionAndCoord(NamedTuple):
    polygon: Polygon
    coord: Coordinate
