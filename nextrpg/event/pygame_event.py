"""
Typed events initiated from `pygame.Event`.
"""

from enum import Enum, auto
from typing import Final

from pygame.constants import (
    KEYDOWN,
    KEYUP,
    QUIT,
    VIDEORESIZE,
)
from pygame.event import Event

from nextrpg.config import KeyCode, config
from nextrpg.draw_on_screen import Size


class PygameEvent:
    """
    Base class for all pygame events.

    Arguments:
        `event`: The pygame event object to wrap
    """

    def __init__(self, event: Event) -> None:
        self._event: Final[Event] = event


class Quit(PygameEvent):
    """
    Represents a quit event from pygame.
    """


class GuiResize(PygameEvent):
    """
    Represents a window resize event from pygame.

    Attributes:
        `size`: The new size of the window.
    """

    def __init__(self, event: Event) -> None:
        super().__init__(event)
        self.size: Final[Size] = Size(event.w, event.h)


class KeyboardKey(Enum):
    """
    Enumeration of supported keyboard keys.

    Attributes:
        `LEFT`: Represents the left arrow key.
        `RIGHT`: Represents the right arrow key.
        `UP`: Represents the up arrow key.
        `DOWN`: Represents the down arrow key.
        `CONFIRM`: Represents the space key.
    """

    UNKNOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    DOWN = auto()
    CONFIRM = auto()

    @classmethod
    def from_pygame(cls, key: KeyCode) -> "KeyboardKey":
        """
        Maps pygame key constant to internal `KeyboardKey` representation.

        Arguments:
            `key`: The pygame key constant to convert

        Returns:
            `KeyboardKey`: The corresponding internal key representation.
                Returns `UNKNOWN` if the key is not supported.
        """
        return {
            config().key_mapping.left: cls.LEFT,
            config().key_mapping.right: cls.RIGHT,
            config().key_mapping.up: cls.UP,
            config().key_mapping.down: cls.DOWN,
            config().key_mapping.confirm: cls.CONFIRM,
        }.get(key, cls.UNKNOWN)


class _KeyPressEvent(PygameEvent):
    def __init__(self, event: Event) -> None:
        super().__init__(event)
        self.key: Final[KeyboardKey] = KeyboardKey.from_pygame(event.key)


class KeyPressDown(_KeyPressEvent):
    """
    Represents a key press down event.

    Attributes:
        `key`: The key pressed down.
    """


class KeyPressUp(_KeyPressEvent):
    """
    Represents a key release event.

    Attributes:
        `key`: The key pressed up.
    """


def to_typed_event(event: Event) -> PygameEvent:
    """
    Creates a typed event wrapper for pygame events.

    Arguments:
        `event`: The pygame event to wrap

    Returns:
        `PygameEvent`: subclass instance based on the event type
    """
    return {
        QUIT: Quit,
        VIDEORESIZE: GuiResize,
        KEYDOWN: KeyPressDown,
        KEYUP: KeyPressUp,
    }.get(event.type, PygameEvent)(event)
