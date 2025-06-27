"""
Handles character movement and collision detection.
"""

from __future__ import annotations

from dataclasses import KW_ONLY, field, replace
from functools import cache, cached_property, singledispatchmethod

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.config import config
from nextrpg.core import Direction, DirectionalOffset, Millisecond, Pixel
from nextrpg.draw_on_screen import Coordinate, DrawOnScreen, Polygon
from nextrpg.event.pygame_event import (
    KeyPressDown,
    KeyPressUp,
    KeyboardKey,
    PygameEvent,
)
from nextrpg.model import Model, internal_field


class CharacterAndVisuals(Model):
    """
    Character and its associated visual elements.

    Args:
        `character`: The main character drawing on screen.

        `below_character_visuals`: Additional drawings below the character.

        `above_character_visuals`: Additional drawings above the character.
    """

    character: DrawOnScreen
    below_character_visuals: list[DrawOnScreen]
    above_character_visuals: list[DrawOnScreen]


class CharacterOnScreen(Model):
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
    speed: Pixel
    collisions: list[Polygon]
    _: KW_ONLY = field()
    _movement_keys: frozenset[KeyboardKey] = internal_field(frozenset)

    @cached_property
    def character_and_visuals(self) -> CharacterAndVisuals:
        """
        Creates drawable representations of the character and visuals.

        Returns:
            `CharacterAndVisuals`: A tuple containing the character's drawable
            representation and any associated visual elements.
        """
        return CharacterAndVisuals(
            DrawOnScreen(self.coordinate, self.character.drawing),
            below_character_visuals=[],
            above_character_visuals=self._collision_visuals,
        )

    @singledispatchmethod
    def event(self, e: PygameEvent) -> CharacterOnScreen:
        """
        Process a pygame event and update the character state accordingly.

        Arguments:
            `e`: The event to process.

        Returns:
            `CharacterOnScreen`: The updated character state
                after processing the event.
        """
        return self

    def _updated_movement_key(
        self, e: KeyPressDown | KeyPressUp
    ) -> frozenset[KeyboardKey]:
        if not e.key in _MOVEMENT_KEYS:
            return self._movement_keys
        assert isinstance(e.key, KeyboardKey)
        if isinstance(e, KeyPressDown):
            return self._movement_keys | {e.key}
        return self._movement_keys - {e.key}

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
        moved_coord = self._move(time_delta)
        return replace(
            self,
            coordinate=moved_coord or self.coordinate,
            character=(
                self.character.move(time_delta)
                if self._movement_keys
                else self.character.idle(time_delta)
            ),
        )

    def _move(self, time_delta: Millisecond) -> Coordinate | None:
        moved_coord = self.coordinate + DirectionalOffset(
            self.character.direction, self.speed * time_delta
        )
        return (
            moved_coord
            if self._movement_keys and self._can_move(time_delta, moved_coord)
            else None
        )

    def _can_move(
        self, time_delta: Millisecond, coordinate: Coordinate
    ) -> bool:
        if (debug := config().debug) and debug.ignore_map_collisions:
            return True

        rect = DrawOnScreen(
            coordinate, self.character.move(time_delta).drawing
        ).rectangle
        hit_coords = {
            Direction.LEFT: {rect.bottom_left, rect.center_left},
            Direction.RIGHT: {rect.bottom_right, rect.center_right},
            Direction.DOWN: {
                rect.bottom_right,
                rect.bottom_center,
                rect.bottom_left,
            },
            Direction.UP: {rect.center_right, rect.center, rect.center_left},
            Direction.UP_LEFT: {
                rect.top_left,
                rect.center_left,
            },
            Direction.UP_RIGHT: {
                rect.top_right,
                rect.center_right,
            },
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
            all(hit_coord not in collision for hit_coord in hit_coords)
            for collision in self.collisions
        )

    @cached_property
    def _collision_visuals(self) -> list[DrawOnScreen]:
        if not (debug := config().debug):
            return []
        return [
            c.fill(debug.collision_rectangle_color) for c in self.collisions
        ]


_MOVEMENT_KEYS = {
    KeyboardKey.LEFT,
    KeyboardKey.RIGHT,
    KeyboardKey.UP,
    KeyboardKey.DOWN,
}

_KEY_TO_DIR = {
    frozenset({KeyboardKey.LEFT, KeyboardKey.UP}): Direction.UP_LEFT,
    frozenset({KeyboardKey.LEFT, KeyboardKey.DOWN}): Direction.DOWN_LEFT,
    frozenset({KeyboardKey.RIGHT, KeyboardKey.UP}): Direction.UP_RIGHT,
    frozenset({KeyboardKey.RIGHT, KeyboardKey.DOWN}): Direction.DOWN_RIGHT,
    frozenset({KeyboardKey.LEFT}): Direction.LEFT,
    frozenset({KeyboardKey.RIGHT}): Direction.RIGHT,
    frozenset({KeyboardKey.UP}): Direction.UP,
    frozenset({KeyboardKey.DOWN}): Direction.DOWN,
}


@cache
def _key_to_dir(current_keys: frozenset[KeyboardKey]) -> Direction | None:
    return next(
        (d for keys, d in _KEY_TO_DIR.items() if keys <= current_keys), None
    )


@CharacterOnScreen.event.register
def _on_key(self, e: KeyPressDown | KeyPressUp) -> CharacterOnScreen:
    updated_keys = self._updated_movement_key(e)
    return replace(
        self,
        character=(
            self.character.turn(direction)
            if (direction := _key_to_dir(updated_keys))
            in config().character.directions
            else self.character
        ),
        _movement_keys=updated_keys,
    )
