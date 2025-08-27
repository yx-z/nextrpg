from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from functools import cache

from pygame.event import Event
from pygame.locals import KEYDOWN, KEYUP, QUIT, VIDEORESIZE

from nextrpg.config.config import config
from nextrpg.config.key_mapping_config import KeyCode
from nextrpg.geometry.dimension import Size


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
    FULL_SCREEN_TOGGLE = auto()
    INCLUDE_FPS_IN_WINDOW_TITLE_TOGGLE = auto()

    @classmethod
    def from_pygame(cls, key: KeyCode) -> KeyboardKey | KeyCode:
        return _key_mapping().get(key, key)


@cache
def _key_mapping() -> dict[KeyCode, KeyboardKey]:
    return {
        config().key_mapping.left: KeyboardKey.LEFT,
        config().key_mapping.right: KeyboardKey.RIGHT,
        config().key_mapping.up: KeyboardKey.UP,
        config().key_mapping.down: KeyboardKey.DOWN,
        config().key_mapping.confirm: KeyboardKey.CONFIRM,
        config().key_mapping.full_screen_toggle: KeyboardKey.FULL_SCREEN_TOGGLE,
        config().key_mapping.include_fps_in_title_toggle: KeyboardKey.INCLUDE_FPS_IN_WINDOW_TITLE_TOGGLE,
    }


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
