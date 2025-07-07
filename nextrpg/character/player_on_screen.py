"""
Handles character movement and collision detection.
"""

from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import override

from nextrpg.character.character_on_screen import (
    CharacterOnScreen,
    MovingCharacterOnScreen,
)
from nextrpg.config import config
from nextrpg.coordinate import Coordinate
from nextrpg.core import Direction, DirectionalOffset, Millisecond
from nextrpg.event.pygame_event import (
    KeyPressDown,
    KeyPressUp,
    KeyboardKey,
    PygameEvent,
)


@dataclass(kw_only=True, frozen=True)
class PlayerOnScreen(MovingCharacterOnScreen):
    _movement_keys: frozenset[KeyboardKey] = field(default_factory=frozenset)

    def event(self, event: PygameEvent) -> CharacterOnScreen:
        if not isinstance(event, (KeyPressDown, KeyPressUp)):
            return self
        updated_keys = self._updated_movement_key(event)
        direction = _key_to_dir(updated_keys)
        character = (
            self.character.turn(direction)
            if direction in config().character.directions
            else self.character
        )
        return replace(self, character=character, _movement_keys=updated_keys)

    def _updated_movement_key(
        self, event: KeyPressDown | KeyPressUp
    ) -> frozenset[KeyboardKey]:
        if event.key not in _MOVEMENT_KEYS:
            return self._movement_keys
        if isinstance(event, KeyPressDown):
            return self._movement_keys | {event.key}
        return self._movement_keys - {event.key}

    @cached_property
    @override
    def moving(self) -> bool:
        return bool(self._movement_keys)

    @override
    def move(self, time_delta: Millisecond) -> Coordinate | None:
        return self.coordinate.shift(
            DirectionalOffset(
                self.character.direction, self.move_speed * time_delta
            )
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
