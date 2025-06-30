"""
Handles character movement and collision detection.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from functools import cached_property
from itertools import product
from typing import override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.config import config
from nextrpg.core import Direction, Millisecond, PixelPerMillisecond
from nextrpg.draw_on_screen import Coordinate, DrawOnScreen, Polygon
from nextrpg.event.pygame_event import PygameEvent
from nextrpg.logger import debug_log


@dataclass
class CharacterOnScreen(ABC):
    """
    Represents a character that can be displayed and moved on screen.

    Handles character movement, collision detection, and event processing for
    character interactions with the game environment.

    Args:
        `character_drawing`: The visual representation of the character.

        `coordinate`: The current position of the character on screen.

        `speed`: Movement speed of the character in pixels.

        `collisions`: List of polygons representing collision boundaries.
    """

    character: CharacterDrawing
    coordinate: Coordinate

    @cached_property
    def draw_on_screen(self) -> DrawOnScreen:
        """
        Creates drawable representations of the character and visuals.

        Returns:
            `CharacterAndVisuals`: A tuple containing the character's drawable
            representation and any associated visual elements.
        """
        return DrawOnScreen(self.coordinate, self.character.drawing)

    @abstractmethod
    def event(self, e: PygameEvent) -> CharacterOnScreen:
        """

        Args:
            e:

        Returns:

        """

    @abstractmethod
    def step(self, time_delta: Millisecond) -> CharacterOnScreen:
        """

        Args:
            time_delta:

        Returns:

        """


@dataclass
class MovingCharacterOnScreen(CharacterOnScreen):
    collisions: list[Polygon]
    move_speed: PixelPerMillisecond = field(
        default_factory=lambda: config().character.move_speed
    )

    @cached_property
    @abstractmethod
    def is_moving(self) -> bool:
        """
        Get whether the character is currently moving.

        Returns:
            `bool`: Whether the character is currently moving.
        """

    @abstractmethod
    def move(self, time_delta: Millisecond) -> Coordinate:
        """
        Move the character based on the current speed and time delta.

        Args:
            `time_delta`: The time that has passed since the last update.

        Returns:
            `Coordinate`: The updated character position after the move step.
        """

    @override
    def step(self, time_delta: Millisecond) -> CharacterOnScreen:
        """
        Update the character's state for a single game step/frame.

        Calculates movement based on currently pressed keys, handles collision
        detection, and updates the character's drawing state (moving or idle).

        Args:
            `time_delta`: The time that has passed since
                the last update, used for calculating movement distance.

        Returns:
            `CharacterOnScreen`: The updated character state after the step.
        """
        moved_coord = self.move(time_delta) if self.is_moving else None
        return replace(
            self,
            character=(
                self.character.move(time_delta)
                if self.is_moving
                else self.character.idle(time_delta)
            ),
            coordinate=(
                moved_coord
                if moved_coord and self._can_move(moved_coord)
                else self.coordinate
            ),
        )

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

        for collision, player_coord in product(self.collisions, hit_coords):
            print(f"{collision=} {player_coord=}")
            if collision.contain(player_coord):
                debug_log(f"Collision: {player_coord} and {collision.points}")
                return False
        return True
