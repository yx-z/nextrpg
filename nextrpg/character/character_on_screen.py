from dataclasses import dataclass, field
from functools import singledispatchmethod
from typing import NamedTuple, Self

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.common_types import (
    Coordinate,
    Direction,
    DirectionalOffset,
    Millisecond,
    Pixel,
    Rectangle,
)
from nextrpg.config import config
from nextrpg.draw_on_screen import DrawOnScreen, Drawing
from nextrpg.event.pygame_event import (
    KeyPressDown,
    KeyPressUp,
    KeyboardKey,
    PygameEvent,
)
from nextrpg.util import clone


class CharacterAndVisuals(NamedTuple):
    character: DrawOnScreen
    visuals: list[DrawOnScreen]


@dataclass(frozen=True)
class CharacterOnScreen:
    character_drawing: CharacterDrawing
    coordinate: Coordinate
    collisions: list[Rectangle]
    speed: Pixel
    _movement_keys: frozenset[KeyboardKey] = field(default_factory=frozenset)

    @property
    def draw_on_screen(self) -> CharacterAndVisuals:
        return CharacterAndVisuals(
            DrawOnScreen(self.coordinate, self.character_drawing.drawing),
            (
                [
                    DrawOnScreen.from_rectangle(
                        c, debug.collision_rectangle_color
                    )
                    for c in self.collisions
                ]
                if (debug := config().debug)
                else []
            ),
        )

    @singledispatchmethod
    def event(self, event: PygameEvent) -> Self:
        return self

    @event.register
    def _on_key(self, e: KeyPressDown | KeyPressUp) -> Self:
        updated_keys = self._on_movement_key(e)
        return clone(
            self,
            character_drawing=(
                self.character_drawing.turn(direction)
                if (direction := _key_to_dir(updated_keys))
                in config().character.directions
                else self.character_drawing
            ),
            _movement_keys=updated_keys,
        )

    def _on_movement_key(
        self, e: KeyPressDown | KeyPressUp
    ) -> frozenset[KeyboardKey]:
        return (
            self._movement_keys | {e.key}
            if isinstance(e, KeyPressDown)
            else (self._movement_keys - {e.key})
        )

    def step(self, time_delta: Millisecond) -> "CharacterOnScreen":
        moved_drawing = self.character_drawing.move(time_delta)
        moved_coordinate = self._move(time_delta, moved_drawing.drawing)
        return clone(
            self,
            coordinate=moved_coordinate or self.coordinate,
            character_drawing=(
                moved_drawing
                if moved_coordinate
                else self.character_drawing.idle(time_delta)
            ),
        )

    def _move(
        self, time_delta: Millisecond, character_drawing: Drawing
    ) -> Coordinate | None:
        """
        Get the moved coordinate if the character can move.

        Returns:
            `Coordinate | None`: Updated `Coordinate` if the character moves.
                `None` otherwise.
        """
        return (
            moved_coord
            if self._movement_keys
            and self._can_move(
                (
                    moved_coord := self.coordinate
                    + DirectionalOffset(
                        self.character_drawing.direction,
                        self.speed * time_delta,
                    )
                ),
                character_drawing,
            )
            else None
        )

    def _can_move(
        self, coordinate: Coordinate, character_drawing: Drawing
    ) -> bool:
        rect = DrawOnScreen(coordinate, character_drawing).visible_rectangle
        hit_coord = {
            Direction.LEFT: {rect.bottom_left},
            Direction.RIGHT: {rect.bottom_right},
            Direction.DOWN: {
                rect.bottom_right,
                rect.bottom_center,
                rect.bottom_left,
            },
            Direction.UP: {rect.center_right, rect.center, rect.center_left},
            Direction.UP_LEFT: {rect.center_left},
            Direction.UP_RIGHT: {rect.center_right},
            Direction.DOWN_LEFT: {rect.bottom_left, rect.bottom_center},
            Direction.DOWN_RIGHT: {rect.bottom_right, rect.bottom_center},
        }[self.character_drawing.direction]
        return all(
            all(h not in collision for h in hit_coord)
            for collision in self.collisions
        )


def _key_to_dir(current_keys: frozenset[KeyboardKey]) -> Direction | None:
    return next(
        (
            direction
            for configured_keys, direction in {
                frozenset(
                    {KeyboardKey.LEFT, KeyboardKey.UP}
                ): Direction.UP_LEFT,
                frozenset(
                    {KeyboardKey.LEFT, KeyboardKey.DOWN}
                ): Direction.DOWN_LEFT,
                frozenset(
                    {KeyboardKey.RIGHT, KeyboardKey.UP}
                ): Direction.UP_RIGHT,
                frozenset(
                    {KeyboardKey.RIGHT, KeyboardKey.DOWN}
                ): Direction.DOWN_RIGHT,
                frozenset({KeyboardKey.LEFT}): Direction.LEFT,
                frozenset({KeyboardKey.RIGHT}): Direction.RIGHT,
                frozenset({KeyboardKey.UP}): Direction.UP,
                frozenset({KeyboardKey.DOWN}): Direction.DOWN,
            }.items()
            if configured_keys <= current_keys
        ),
        None,
    )
