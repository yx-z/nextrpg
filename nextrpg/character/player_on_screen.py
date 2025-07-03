"""
Handles character movement and collision detection.
"""

from dataclasses import dataclass, field, replace
from functools import cached_property, singledispatchmethod
from typing import override

from nextrpg.character.character_on_screen import (
    CharacterOnScreen,
    MovingCharacterOnScreen,
)
from nextrpg.config import config
from nextrpg.core import Direction, DirectionalOffset, Millisecond
from nextrpg.draw_on_screen import Coordinate
from nextrpg.event.pygame_event import (
    KeyPressDown,
    KeyPressUp,
    KeyboardKey,
    PygameEvent,
)


@dataclass
class PlayerOnScreen(MovingCharacterOnScreen):
    _movement_keys: frozenset[KeyboardKey] = field(default_factory=frozenset)

    @override
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
        if e.key not in _MOVEMENT_KEYS:
            return self._movement_keys
        assert isinstance(e.key, KeyboardKey)
        if isinstance(e, KeyPressDown):
            return self._movement_keys | {e.key}
        return self._movement_keys - {e.key}

    @cached_property
    @override
    def is_moving(self) -> bool:
        return bool(self._movement_keys)

    @override
    def move(self, time_delta: Millisecond) -> Coordinate | None:
        return self.coordinate + DirectionalOffset(
            self.character.direction, self.move_speed * time_delta
        )


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


def _key_to_dir(current_keys: frozenset[KeyboardKey]) -> Direction | None:
    return next(
        (d for keys, d in _KEY_TO_DIR.items() if keys <= current_keys), None
    )


@PlayerOnScreen.event.register
def _on_key(self, e: KeyPressDown | KeyPressUp) -> CharacterOnScreen:
    updated_keys = self._updated_movement_key(e)
    direction = _key_to_dir(updated_keys)
    return replace(
        self,
        character=(
            self.character.turn(direction)
            if direction in config().character.directions
            else self.character
        ),
        _movement_keys=updated_keys,
    )