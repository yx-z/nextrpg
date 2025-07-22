"""
Moving character implementation for `nextrpg`.

This module provides the base class for characters that can move around the game
world. It handles movement calculations, collision detection, and character
state management during movement.

Features:
    - Abstract movement interface for characters
    - Collision detection against polygon boundaries
    - Movement speed and direction handling
    - Character animation state management
    - Event-driven movement controls
"""

from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, dataclass, field, replace
from typing import NamedTuple, Self, override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import PixelPerMillisecond
from nextrpg.core.direction import Direction
from nextrpg.core.logger import Logger
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw_on_screen import DrawOnScreen, Polygon
from nextrpg.global_config.global_config import config
from nextrpg.core.model import not_constructor_below

logger = Logger("MovingCharacterOnScreen")


@dataclass(kw_only=True, frozen=True)
class MovingCharacterOnScreen(CharacterOnScreen, ABC):
    """
    Abstract base class for characters that can move around the game world.

    This class provides the foundation for movement-capable characters,
    including collision detection, movement calculations, and proper
    animation state management. It's designed to be extended by both
    player characters and NPCs that need movement capabilities.

    Arguments:
        `collisions`: Tuple of polygons representing collision boundaries
            that the character cannot pass through.

        `move_speed`: Movement speed in pixels per millisecond.
            Defaults to the global character configuration.

    Example:
        ```python
        class PlayerCharacter(MovingCharacterOnScreen):
            @cached_property
            def moving(self) -> bool:
                return bool(self.pressed_keys)

            def move(self, time_delta: Millisecond) -> Coordinate:
                return self.calculate_new_position(time_delta)
        ```
    """

    collisions: tuple[Polygon, ...]
    move_speed: PixelPerMillisecond = field(
        default_factory=lambda: config().character.move_speed
    )
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
    def moving(self) -> bool:
        """
        Get whether the character is currently moving.

        This property should be implemented by subclasses to determine
        if the character should be in a moving state. This affects
        both animation and movement calculations.

        Returns:
            `bool`: Whether the character is currently moving.

        Example:
            ```python
            @cached_property
            def moving(self) -> bool:
                return bool(self.pressed_movement_keys)
            ```
        """

    @abstractmethod
    def move(self, time_delta: Millisecond) -> Coordinate:
        """
        Calculate the new position after movement.

        This method should be implemented by subclasses to calculate
        the character's new position based on current movement state,
        speed, and time delta. The returned coordinate will be used
        if no collision is detected.

        Arguments:
            `time_delta`: The time that has passed since the last update
                in milliseconds.

        Returns:
            `Coordinate`: The updated character position after the move step.

        Example:
            ```python
            def move(self, time_delta: Millisecond) -> Coordinate:
                distance = self.move_speed * time_delta
                return self.coordinate.shift(
                    DirectionalOffset(self.direction, distance)
                )
            ```
        """

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
        """
        Check if the character can move to the specified coordinate.

        Performs collision detection against all collision polygons
        to determine if the movement is allowed. Uses different
        collision points based on the character's current direction.

        Arguments:
            `coordinate`: The target coordinate to check for movement.

        Returns:
            `bool`: Whether the character can move to the coordinate.

        Example:
            ```python
            if character._can_move(new_position):
                character = character.move_to(new_position)
            ```
        """
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
            logger.debug(f"Collision {coord} and {collision.points}")
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
