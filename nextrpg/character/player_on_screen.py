from dataclasses import KW_ONLY, dataclass, field, replace
from typing import Self, override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.moving_character_on_screen import MovingCharacterOnScreen
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dataclass_with_init import not_constructor_below
from nextrpg.core.direction import Direction, DirectionalOffset
from nextrpg.core.time import Millisecond
from nextrpg.event.pygame_event import (
    KeyPressDown,
    KeyPressUp,
    KeyboardKey,
    PygameEvent,
)
from nextrpg.global_config.global_config import config


@dataclass(frozen=True)
class PlayerOnScreen(MovingCharacterOnScreen):
    _: KW_ONLY = not_constructor_below()
    _movement_keys: frozenset[KeyboardKey] = field(default_factory=frozenset)

    @override
    def start_event(self, character: CharacterOnScreen) -> Self:
        start_event = super().start_event(character)
        return replace(start_event, _movement_keys=frozenset())

    def event(self, event: PygameEvent) -> Self:
        if self._event_started or not isinstance(
            event, (KeyPressDown, KeyPressUp)
        ):
            return self

        updated_keys = self._updated_movement_key(event)
        direction = _key_to_dir(updated_keys)
        character = (
            self.character.turn(direction)
            if direction in config().player.directions
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

    @property
    @override
    def moving(self) -> bool:
        return bool(self._movement_keys)

    @override
    def move(self, time_delta: Millisecond) -> Coordinate | None:
        directional_offset = DirectionalOffset(
            self.character.direction, self.config.move_speed * time_delta
        )
        return self.coordinate + directional_offset

    @override
    def can_move(
        self, coordinate: Coordinate, others: tuple[CharacterOnScreen, ...]
    ) -> bool:
        if (debug := config().debug) and not debug.player_collide_with_others:
            return True
        return super().can_move(coordinate, others)


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
    for keys, d in _KEY_TO_DIR.items():
        if keys <= current_keys:
            return d
    return None
