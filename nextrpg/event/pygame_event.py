"""
Typed events initiated from `pygame.Event`.
"""

from dataclasses import dataclass
from enum import Enum, auto
from functools import cached_property

from pygame.event import Event
from pygame.locals import KEYDOWN, KEYUP, QUIT, VIDEORESIZE

from nextrpg.config import KeyCode, config
from nextrpg.draw_on_screen import Size


@dataclass
class PygameEvent:
    """
    Base class for all pygame events.

    Arguments:
        `event`: The pygame event object to wrap
    """

    event: Event


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

    @cached_property
    def size(self) -> Size:
        return Size(self.event.w, self.event.h)


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
    GUI_MODE_TOGGLE = auto()

    @classmethod
    def from_pygame(cls, key: KeyCode) -> KeyboardKey | KeyCode:
        """
        Maps pygame key constant to internal `KeyboardKey` representation.

        Arguments:
            `key`: The pygame key constant to convert

        Returns:
            `KeyboardKey` | `KeyCode`: The corresponding internal
                key representation. If the key is not supported,
                returns the raw key code.
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
    @cached_property
    def key(self) -> KeyboardKey | KeyCode:
        return KeyboardKey.from_pygame(self.event.key)


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