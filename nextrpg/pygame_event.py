"""
Typed event system for pygame events in NextRPG.

This module provides a type-safe wrapper system for pygame events,
converting raw pygame events into strongly-typed event objects.
It includes event classes for keyboard input, window management,
and game control events.

The event system features:
- Type-safe event wrappers for all pygame events
- Keyboard key mapping and enumeration
- Window resize event handling
- Quit event processing
- Integration with the key mapping configuration system

Example:
    ```python
    from nextrpg.pygame_event import to_typed_event, KeyPressDown
    from nextrpg.keyboard_key import KeyboardKey

    # Convert pygame event to typed event
    typed_event = to_typed_event(pygame_event)

    # Handle specific event types
    if isinstance(typed_event, KeyPressDown):
        if typed_event.key == KeyboardKey.LEFT:
            # Handle left arrow press
            pass
    ```
"""

from dataclasses import dataclass
from enum import Enum, auto
from functools import cached_property

from pygame.event import Event
from pygame.locals import KEYDOWN, KEYUP, QUIT, VIDEORESIZE

from nextrpg.draw_on_screen import Size
from nextrpg.global_config import config
from nextrpg.key_mapping_config import KeyCode
from nextrpg.model import export


@export
@dataclass(frozen=True)
class PygameEvent:
    """
    Base class for all pygame events.

    This class provides a type-safe wrapper around pygame events,
    allowing for better type checking and event handling in the
    NextRPG framework.

    Arguments:
        `event`: The pygame event object to wrap.

    Example:
        ```python
        from nextrpg.pygame_event import PygameEvent

        # Create a typed event wrapper
        typed_event = PygameEvent(pygame_event)
        ```
    """

    event: Event


@export
class Quit(PygameEvent):
    """
    Represents a quit event from pygame.

    This event is triggered when the user attempts to close the
    game window or when the game is requested to terminate.

    Example:
        ```python
        from nextrpg.pygame_event import Quit

        if isinstance(event, Quit):
            # Handle game quit request
            game.running = False
        ```
    """


@export
class GuiResize(PygameEvent):
    """
    Represents a window resize event from pygame.

    This event is triggered when the game window is resized by
    the user or programmatically.

    Attributes:
        `size`: The new size of the window.

    Example:
        ```python
        from nextrpg.pygame_event import GuiResize

        if isinstance(event, GuiResize):
            new_size = event.size
            # Update game layout for new window size
        ```
    """

    @cached_property
    def size(self) -> Size:
        """
        Get the new window size from the resize event.

        Returns:
            `Size`: The new width and height of the window.
        """
        return Size(self.event.w, self.event.h)


@export
class KeyboardKey(Enum):
    """
    Enumeration of supported keyboard keys.

    This enum provides a standardized set of keyboard keys that
    are supported by the NextRPG framework. It maps pygame key
    constants to internal key representations.

    Attributes:
        `UNKNOWN`: Represents an unrecognized key.
        `LEFT`: Represents the left arrow key.
        `RIGHT`: Represents the right arrow key.
        `UP`: Represents the up arrow key.
        `DOWN`: Represents the down arrow key.
        `CONFIRM`: Represents the space key or enter key.
        `GUI_MODE_TOGGLE`: Represents the key to toggle GUI mode.

    Example:
        ```python
        from nextrpg.pygame_event import KeyboardKey

        # Check for specific keys
        if key == KeyboardKey.LEFT:
            # Handle left arrow
            pass
        elif key == KeyboardKey.CONFIRM:
            # Handle confirm action
            pass
        ```
    """

    UNKNOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    DOWN = auto()
    CONFIRM = auto()
    GUI_MODE_TOGGLE = auto()

    @classmethod
    def from_pygame(cls, key: KeyCode) -> KeyboardKey | KeyCode:
        """
        Maps pygame key constant to internal `KeyboardKey` representation.

        Converts pygame key constants to the standardized keyboard
        key enumeration. If the key is not recognized, returns the
        raw key code for custom handling.

        Arguments:
            `key`: The pygame key constant to convert.

        Returns:
            `KeyboardKey | KeyCode`: The corresponding internal
                key representation. If the key is not supported,
                returns the raw key code.

        Example:
            ```python
            from nextrpg.pygame_event import KeyboardKey

            # Convert pygame key to internal representation
            internal_key = KeyboardKey.from_pygame(pygame.K_LEFT)
            # Returns KeyboardKey.LEFT
            ```
        """
        return {
            config().key_mapping.left: cls.LEFT,
            config().key_mapping.right: cls.RIGHT,
            config().key_mapping.up: cls.UP,
            config().key_mapping.down: cls.DOWN,
            config().key_mapping.confirm: cls.CONFIRM,
            config().key_mapping.gui_mode_toggle: cls.GUI_MODE_TOGGLE,
        }.get(key, key)


class _KeyPressEvent(PygameEvent):
    """
    Base class for keyboard press events.

    This internal class provides common functionality for both
    key press and key release events.
    """

    @cached_property
    def key(self) -> KeyboardKey | KeyCode:
        """
        Get the key associated with this event.

        Returns:
            `KeyboardKey | KeyCode`: The key that was pressed or released.
        """
        return KeyboardKey.from_pygame(self.event.key)


@export
class KeyPressDown(_KeyPressEvent):
    """
    Represents a key press down event.

    This event is triggered when a key is first pressed down.

    Attributes:
        `key`: The key that was pressed down.

    Example:
        ```python
        from nextrpg.pygame_event import KeyPressDown
        from nextrpg.keyboard_key import KeyboardKey

        if isinstance(event, KeyPressDown):
            if event.key == KeyboardKey.SPACE:
                # Handle space key press
                player.jump()
        ```
    """


@export
class KeyPressUp(_KeyPressEvent):
    """
    Represents a key release event.

    This event is triggered when a key is released after being
    pressed down.

    Attributes:
        `key`: The key that was released.

    Example:
        ```python
        from nextrpg.pygame_event import KeyPressUp
        from nextrpg.keyboard_key import KeyboardKey

        if isinstance(event, KeyPressUp):
            if event.key == KeyboardKey.SPACE:
                # Handle space key release
                player.stop_jump()
        ```
    """


@export
def to_typed_event(event: Event) -> PygameEvent:
    """
    Creates a typed event wrapper for pygame events.

    Converts raw pygame events into strongly-typed event objects
    that provide better type safety and easier event handling.

    Arguments:
        `event`: The pygame event to wrap.

    Returns:
        `PygameEvent`: A subclass instance based on the event type.

    Example:
        ```python
        from nextrpg.pygame_event import to_typed_event, Quit, KeyPressDown

        # Convert pygame event to typed event
        typed_event = to_typed_event(pygame_event)

        # Handle different event types
        if isinstance(typed_event, Quit):
            # Handle quit event
            pass
        elif isinstance(typed_event, KeyPressDown):
            # Handle key press
            pass
        ```
    """
    return {
        QUIT: Quit,
        VIDEORESIZE: GuiResize,
        KEYDOWN: KeyPressDown,
        KEYUP: KeyPressUp,
    }.get(event.type, PygameEvent)(event)
