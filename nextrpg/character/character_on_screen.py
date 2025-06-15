from functools import singledispatchmethod
from typing import Final, NamedTuple

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


class CharacterAndVisuals(NamedTuple):
    character: DrawOnScreen
    visuals: list[DrawOnScreen]


class CharacterOnScreen:
    def __init__(
        self,
        character_sprite: CharacterDrawing,
        coordinate: Coordinate,
        direction: Direction,
        collisions: list[Rectangle],
        speed: Pixel | None = None,
    ) -> None:
        self._sprite: CharacterDrawing = character_sprite
        self._speed: Final[Pixel] = (
            config().character.default_move_speed if speed is None else speed
        )
        self._collisions: Final[list[Rectangle]] = collisions
        self._coordinate = coordinate
        self._direction = direction
        self._movement_keys: set[KeyboardKey] = set()

    @property
    def direction(self) -> Direction:
        """
        Gets the current direction of the character.

        Returns:
            `Direction`: The current direction that the character is facing.
        """
        return self._direction

    @property
    def coordinate(self) -> Coordinate:
        """
        Gets the current coordinate of the character.

        Returns:
            `Coordinate`: The current position of the character on screen.
        """
        return self._coordinate

    @singledispatchmethod
    def event(self, e: PygameEvent) -> None:
        pass

    @event.register
    def _turn_direction(self, e: KeyPressDown | KeyPressUp) -> None:
        if (key := e.key) not in _MOVEMENT_KEYS:
            return

        if isinstance(e, KeyPressDown):
            self._movement_keys.add(key)
        else:
            self._movement_keys.discard(key)

        if (
            d := _DIRECTIONS.get(frozenset(self._movement_keys))
        ) in config().character.move_directions:
            self._direction = d

    def draw_on_screen(self, time_delta: Millisecond) -> CharacterAndVisuals:
        if self._move(
            time_delta, self._sprite.peek_move(time_delta, self.direction)
        ):
            self._sprite = self._sprite.move(time_delta, self.direction)
            drawing = self._sprite.draw_move(self.direction)
        else:
            self._sprite = self._sprite.idle(time_delta, self.direction)
            drawing = self._sprite.draw_idle(self.direction)

        return CharacterAndVisuals(
            DrawOnScreen(self.coordinate, drawing),
            (
                [DrawOnScreen.from_rectangle(c) for c in self._collisions]
                if config().debug
                else []
            ),
        )

    def _move(self, time_delta: Millisecond, drawing: Drawing) -> bool:
        """
        Returns:
            `bool`: Whether the character is moving,
                based on current movement keys.
        """
        if not self._movement_keys:
            return False
        coord = self.coordinate + DirectionalOffset(
            self.direction, self._speed * time_delta
        )
        if is_moving := self._can_move(coord, drawing):
            self._coordinate = coord
        return is_moving

    def _can_move(self, coordinate: Coordinate, drawing: Drawing) -> bool:
        rect = DrawOnScreen(coordinate, drawing).visible_rectangle
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
        }[self.direction]
        return all(
            all(h not in collision for h in hit_coord)
            for collision in self._collisions
        )


_MOVEMENT_KEYS = {
    KeyboardKey.LEFT,
    KeyboardKey.RIGHT,
    KeyboardKey.UP,
    KeyboardKey.DOWN,
}

_DIRECTIONS: dict[frozenset[KeyboardKey], Direction] = {
    frozenset({KeyboardKey.LEFT}): Direction.LEFT,
    frozenset({KeyboardKey.RIGHT}): Direction.RIGHT,
    frozenset({KeyboardKey.UP}): Direction.UP,
    frozenset({KeyboardKey.DOWN}): Direction.DOWN,
    frozenset({KeyboardKey.LEFT, KeyboardKey.UP}): Direction.UP_LEFT,
    frozenset({KeyboardKey.LEFT, KeyboardKey.DOWN}): Direction.DOWN_LEFT,
    frozenset({KeyboardKey.RIGHT, KeyboardKey.UP}): Direction.UP_RIGHT,
    frozenset({KeyboardKey.RIGHT, KeyboardKey.DOWN}): Direction.DOWN_RIGHT,
}
