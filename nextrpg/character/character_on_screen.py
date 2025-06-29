"""
Handles character movement and collision detection.
"""

from dataclasses import dataclass
from functools import cached_property

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.config import config
from nextrpg.core import Direction, Pixel, PixelPerMillisecond
from nextrpg.draw_on_screen import Coordinate, DrawOnScreen, Polygon


@dataclass
class CharacterOnScreen:
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
    speed: PixelPerMillisecond
    collisions: list[Polygon]

    @cached_property
    def draw_on_screen(self) -> DrawOnScreen:
        """
        Creates drawable representations of the character and visuals.

        Returns:
            `CharacterAndVisuals`: A tuple containing the character's drawable
            representation and any associated visual elements.
        """
        return DrawOnScreen(self.coordinate, self.character.drawing)

    def can_move(self, coordinate: Coordinate) -> bool:
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
        return all(
            all(not collision.contain(hit_coord) for hit_coord in hit_coords)
            for collision in self.collisions
        )
