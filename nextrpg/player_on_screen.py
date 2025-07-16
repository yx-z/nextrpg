"""
Player character implementation for `nextrpg`.

This module provides the `PlayerOnScreen` class that handles player character
movement, input processing, and interaction with the game world. It extends the
base moving character functionality with keyboard input handling and
player-specific behaviors.

Features:
    - Keyboard input processing for movement
    - Eight-directional movement support
    - Key press and release event handling
    - Movement state management
    - Collision detection integration
"""

from dataclasses import KW_ONLY, dataclass, field, replace
from functools import cached_property
from typing import Self, override

from nextrpg.model import not_constructor_below
from nextrpg.character_on_screen import CharacterOnScreen
from nextrpg.coordinate import Coordinate
from nextrpg.core import Direction, DirectionalOffset, Millisecond
from nextrpg.global_config import config
from nextrpg.model import export
from nextrpg.moving_character_on_screen import MovingCharacterOnScreen
from nextrpg.pygame_event import (
    KeyboardKey,
    KeyPressDown,
    KeyPressUp,
    PygameEvent,
)


@export
@dataclass(kw_only=True, frozen=True)
class PlayerOnScreen(MovingCharacterOnScreen):
    """
    Player character that responds to keyboard input for movement.

    This class extends `MovingCharacterOnScreen` to provide player-specific
    functionality including keyboard input processing, movement state
    management, and proper character direction handling based on
    currently pressed movement keys.

    The player supports movement in all eight directions (orthogonal
    and diagonal) with proper key combination handling. Movement
    keys are tracked and the character's direction is updated
    accordingly.

    Arguments:
        `_movement_keys`: Internal set of currently pressed movement keys.
            This is managed automatically by the event system.

    Example:
        ```python
        from nextrpg.player_on_screen import PlayerOnScreen
        from nextrpg.character_drawing import CharacterDrawing

        player = PlayerOnScreen(
            character=CharacterDrawing(drawing=player_sprite),
            coordinate=Coordinate(100, 100),
            collisions=map_collisions
        )

        # Handle keyboard events
        player = player.event(key_press_event)
        ```
    """

    _: KW_ONLY = not_constructor_below()
    _movement_keys: frozenset[KeyboardKey] = field(default_factory=frozenset)

    @override
    def start_event(self, character: CharacterOnScreen) -> Self:
        """
        Start an event interaction with another character.

        When starting an event, the player stops all movement and
        turns to face the other character. This ensures proper
        interaction positioning.

        Arguments:
            `character`: The character to start an event with.

        Returns:
            `PlayerOnScreen`: The updated player state with movement stopped.

        Example:
            ```python
            # Start interaction with NPC
            player = player.start_event(npc)
            ```
        """
        start_event = super().start_event(character)
        return replace(start_event, _movement_keys=frozenset())

    def event(self, event: PygameEvent) -> Self:
        """
        Process pygame events for player input.

        Handles key press and release events for movement keys,
        updates the internal movement key state, and adjusts
        the character's direction based on currently pressed keys.

        Arguments:
            `event`: The pygame event to process.

        Returns:
            `PlayerOnScreen`: The updated player state after processing the event.

        Example:
            ```python
            # Handle keyboard input
            player = player.event(key_press_event)
            ```
        """
        is_key_press = isinstance(event, (KeyPressDown, KeyPressUp))
        if self._event_triggered or not is_key_press:
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
        """
        Update the set of currently pressed movement keys.

        Adds keys on press events and removes them on release events.
        Only processes keys that are defined as movement keys.

        Arguments:
            `event`: The key press or release event to process.

        Returns:
            `frozenset[KeyboardKey]`: The updated set of pressed movement keys.

        Example:
            ```python
            keys = player._updated_movement_key(key_event)
            ```
        """
        if event.key not in _MOVEMENT_KEYS:
            return self._movement_keys
        if isinstance(event, KeyPressDown):
            return self._movement_keys | {event.key}
        return self._movement_keys - {event.key}

    @property
    @override
    def moving(self) -> bool:
        """
        Get whether the player is currently moving.

        Determines movement state based on whether any movement
        keys are currently pressed.

        Returns:
            `bool`: Whether the player is currently moving.

        Example:
            ```python
            if player.moving:
                # Handle movement animation
                pass
            ```
        """
        return bool(self._movement_keys)

    @override
    def move(self, time_delta: Millisecond) -> Coordinate | None:
        """
        Calculate the player's new position based on movement.

        Uses the character's current direction and movement speed
        to calculate the new position after the time delta.

        Arguments:
            `time_delta`: The time elapsed since the last update
                in milliseconds.

        Returns:
            `Coordinate | None`: The new position, or None if not moving.

        Example:
            ```python
            new_pos = player.move(time_delta)
            if new_pos and player._can_move(new_pos):
                player = player.move_to(new_pos)
            ```
        """
        directional_offset = DirectionalOffset(
            self.character.direction, self.move_speed * time_delta
        )
        return self.coordinate.shift(directional_offset)


# Movement key configuration
_MOVEMENT_KEYS = {
    KeyboardKey.LEFT,
    KeyboardKey.RIGHT,
    KeyboardKey.UP,
    KeyboardKey.DOWN,
}

# Key combination to direction mapping
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
    """
    Convert a set of pressed keys to a movement direction.

    Maps key combinations to the appropriate movement direction,
    supporting both single key and diagonal movement combinations.

    Arguments:
        `current_keys`: The set of currently pressed movement keys.

    Returns:
        `Direction | None`: The movement direction, or None if no
            valid combination is pressed.

    Example:
        ```python
        direction = _key_to_dir({KeyboardKey.UP, KeyboardKey.RIGHT})
        # Returns Direction.UP_RIGHT
        ```
    """
    for keys, d in _KEY_TO_DIR.items():
        if keys <= current_keys:
            return d
    return None
