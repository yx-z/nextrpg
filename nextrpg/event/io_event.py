from dataclasses import dataclass
from enum import Enum, auto
from functools import cache, cached_property
from typing import TypeIs

from pygame.event import Event, post
from pygame.locals import KEYDOWN, KEYUP, QUIT, VIDEORESIZE

from nextrpg.config.config import config
from nextrpg.config.key_mapping_config import KeyCode
from nextrpg.geometry.dimension import Size


@dataclass(frozen=True)
class IoEvent:
    event: Event


class Quit(IoEvent):
    pass


class WindowResize(IoEvent):
    @cached_property
    def size(self) -> Size:
        return Size(self.event.w, self.event.h)


class KeyboardKey(Enum):
    UNKNOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    DOWN = auto()
    CONFIRM = auto()
    CANCEL = auto()
    FULL_SCREEN_TOGGLE = auto()
    INCLUDE_FPS_IN_WINDOW_TITLE_TOGGLE = auto()

    @classmethod
    def from_pygame(cls, key: KeyCode) -> KeyboardKey | KeyCode:
        return _key_mapping().get(key, key)


def is_key_press(event: IoEvent, key: KeyboardKey) -> TypeIs[KeyPressDown]:
    return isinstance(event, KeyPressDown) and event.key == key


@cache
def _key_mapping() -> dict[KeyCode, KeyboardKey]:
    return {
        config().key_mapping.left: KeyboardKey.LEFT,
        config().key_mapping.right: KeyboardKey.RIGHT,
        config().key_mapping.up: KeyboardKey.UP,
        config().key_mapping.down: KeyboardKey.DOWN,
        config().key_mapping.confirm: KeyboardKey.CONFIRM,
        config().key_mapping.cancel: KeyboardKey.CANCEL,
        config().key_mapping.full_screen_toggle: KeyboardKey.FULL_SCREEN_TOGGLE,
        config().key_mapping.include_fps_in_title_toggle: KeyboardKey.INCLUDE_FPS_IN_WINDOW_TITLE_TOGGLE,
    }


class _KeyPressEvent(IoEvent):
    @cached_property
    def key(self) -> KeyboardKey | KeyCode:
        return KeyboardKey.from_pygame(self.event.key)


class KeyPressDown(_KeyPressEvent):
    pass


class KeyPressUp(_KeyPressEvent):
    pass


def to_io_event(event: Event) -> IoEvent:
    return {
        QUIT: Quit,
        VIDEORESIZE: WindowResize,
        KEYDOWN: KeyPressDown,
        KEYUP: KeyPressUp,
    }.get(event.type, IoEvent)(event)


def quit() -> None:
    post(Event(QUIT))
