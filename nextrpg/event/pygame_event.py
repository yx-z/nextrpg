from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from pygame.event import Event, post
from pygame.locals import KEYDOWN, KEYUP, QUIT, VIDEORESIZE

from nextrpg.core.dimension import Size
from nextrpg.global_config.global_config import config
from nextrpg.global_config.key_mapping_config import KeyCode


@dataclass(frozen=True)
class PygameEvent:
    event: Event


class Quit(PygameEvent):
    pass


class WindowResize(PygameEvent):
    @property
    def size(self) -> Size:
        return Size(self.event.w, self.event.h)


class KeyboardKey(Enum):
    UNKNOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    DOWN = auto()
    CONFIRM = auto()
    WINDOW_MODE_TOGGLE = auto()

    @classmethod
    def from_pygame(cls, key: KeyCode) -> KeyboardKey | KeyCode:
        return {
            config().key_mapping.left: cls.LEFT,
            config().key_mapping.right: cls.RIGHT,
            config().key_mapping.up: cls.UP,
            config().key_mapping.down: cls.DOWN,
            config().key_mapping.confirm: cls.CONFIRM,
            config().key_mapping.gui_mode_toggle: cls.WINDOW_MODE_TOGGLE,
        }.get(key, key)


class _KeyPressEvent(PygameEvent):
    @property
    def key(self) -> KeyboardKey | KeyCode:
        return KeyboardKey.from_pygame(self.event.key)


class KeyPressDown(_KeyPressEvent):
    pass


class KeyPressUp(_KeyPressEvent):
    pass


def to_typed_event(event: Event) -> PygameEvent:
    return {
        QUIT: Quit,
        VIDEORESIZE: WindowResize,
        KEYDOWN: KeyPressDown,
        KEYUP: KeyPressUp,
    }.get(event.type, PygameEvent)(event)


def trigger_quit() -> None:
    post(Event(QUIT))
