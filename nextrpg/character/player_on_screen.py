from collections.abc import Collection
from dataclasses import KW_ONLY, dataclass, field, replace
from functools import cached_property
from typing import Self, override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.moving_character_on_screen import MovingCharacterOnScreen
from nextrpg.character.player_spec import PlayerSpec
from nextrpg.config.character.player_config import PlayerConfig
from nextrpg.config.config import config
from nextrpg.config.system.key_mapping_config import (
    KeyMapping,
    KeyMappingConfig,
)
from nextrpg.core.dataclass_with_default import private_init_below
from nextrpg.core.time import Millisecond
from nextrpg.event.base_event import BaseEvent
from nextrpg.event.io_event import KeyPressDown, KeyPressUp
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.direction import Direction
from nextrpg.geometry.directional_offset import DirectionalOffset


@dataclass(frozen=True, kw_only=True)
class PlayerOnScreen(MovingCharacterOnScreen):
    spec: PlayerSpec
    config: PlayerConfig = field(
        default_factory=lambda: config().character.player
    )
    _: KW_ONLY = private_init_below()
    _movement_keys: frozenset[KeyMapping] = field(default_factory=frozenset)

    @cached_property
    def stop(self) -> Self:
        return replace(self, _movement_keys=frozenset())

    @override
    def start_event(self, character: CharacterOnScreen) -> Self:
        return super().start_event(character).stop

    def event(self, event: BaseEvent) -> Self:
        if self._event_started or not isinstance(
            event, (KeyPressDown, KeyPressUp)
        ):
            return self

        updated_keys = self._updated_movement_key(event)
        direction = _key_to_dir(updated_keys)
        character_drawing = (
            self.character_drawing.turn(direction)
            if direction in self.config.directions
            else self.character_drawing
        )
        return replace(
            self,
            character_drawing=character_drawing,
            _movement_keys=updated_keys,
        )

    def _updated_movement_key(
        self, event: KeyPressDown | KeyPressUp
    ) -> frozenset[KeyMapping]:
        if event.key_mapping not in _MOVEMENT_KEYS:
            return self._movement_keys
        if isinstance(event, KeyPressDown):
            return self._movement_keys | {event.key_mapping}
        return self._movement_keys - {event.key_mapping}

    @override
    @cached_property
    def moving(self) -> bool:
        return bool(self._movement_keys)

    @override
    def move(self, time_delta: Millisecond) -> Coordinate | None:
        directional_offset = DirectionalOffset(
            self.character_drawing.direction,
            self.spec.config.move_speed * time_delta,
        )
        return self.coordinate + directional_offset

    @override
    def can_move(
        self, coordinate: Coordinate, others: Collection[CharacterOnScreen]
    ) -> bool:
        if (debug := config().debug) and not debug.player_collide_with_others:
            return True
        return super().can_move(coordinate, others)


_MOVEMENT_KEYS = (
    KeyMappingConfig.left,
    KeyMappingConfig.right,
    KeyMappingConfig.up,
    KeyMappingConfig.down,
)

_KEY_TO_DIR = {
    frozenset({KeyMappingConfig.left, KeyMappingConfig.up}): Direction.UP_LEFT,
    frozenset(
        {KeyMappingConfig.left, KeyMappingConfig.down}
    ): Direction.DOWN_LEFT,
    frozenset(
        {KeyMappingConfig.right, KeyMappingConfig.up}
    ): Direction.UP_RIGHT,
    frozenset(
        {KeyMappingConfig.right, KeyMappingConfig.down}
    ): Direction.DOWN_RIGHT,
    frozenset({KeyMappingConfig.left}): Direction.LEFT,
    frozenset({KeyMappingConfig.right}): Direction.RIGHT,
    frozenset({KeyMappingConfig.up}): Direction.UP,
    frozenset({KeyMappingConfig.down}): Direction.DOWN,
}


def _key_to_dir(current_keys: frozenset[KeyMapping]) -> Direction | None:
    for keys, d in _KEY_TO_DIR.items():
        if keys <= current_keys:
            return d
    return None
