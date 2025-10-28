from dataclasses import KW_ONLY, dataclass, field, replace
from functools import cached_property
from typing import Self, override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.moving_character_on_screen import MovingCharacterOnScreen
from nextrpg.config.character.player_config import PlayerConfig
from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default import private_init_below
from nextrpg.core.time import Millisecond
from nextrpg.event.io_event import (
    IoEvent,
    KeyboardKey,
    KeyPressDown,
    KeyPressUp,
)
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.direction import Direction, DirectionalOffset


@dataclass(frozen=True)
class PlayerOnScreen(MovingCharacterOnScreen):
    config: PlayerConfig = field(default_factory=lambda: config().player)
    _: KW_ONLY = private_init_below()
    _movement_keys: frozenset[KeyboardKey] = field(default_factory=frozenset)

    @cached_property
    def stop(self) -> Self:
        return replace(self, _movement_keys=frozenset())

    @override
    def start_event(self, character: CharacterOnScreen) -> Self:
        return super().start_event(character).stop

    def event(self, event: IoEvent) -> Self:
        if self._event_started or not isinstance(
            event, (KeyPressDown, KeyPressUp)
        ):
            return self

        updated_keys = self._updated_movement_key(event)
        direction = _key_to_dir(updated_keys)
        character = (
            self.character.turn(direction)
            if direction in self.config.directions
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

    @override
    @cached_property
    def moving(self) -> bool:
        return bool(self._movement_keys)

    @override
    def move(self, time_delta: Millisecond) -> Coordinate | None:
        directional_offset = DirectionalOffset(
            self.character.direction, self.spec.config.move_speed * time_delta
        )
        return self.coordinate + directional_offset

    @override
    def can_move(
        self, top_left: Coordinate, others: tuple[CharacterOnScreen, ...]
    ) -> bool:
        if (debug := config().debug) and not debug.player_collide_with_others:
            return True
        return super().can_move(top_left, others)


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
