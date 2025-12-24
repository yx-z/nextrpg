from dataclasses import dataclass, fields, is_dataclass

from pygame import (
    K_DOWN,
    K_ESCAPE,
    K_F1,
    K_F2,
    K_F3,
    K_LEFT,
    K_RETURN,
    K_RIGHT,
    K_SPACE,
    K_TAB,
    K_UP,
    K_a,
    K_d,
    K_s,
    K_w,
)

type KeyCode = int


@dataclass(frozen=True)
class KeyMapping:
    name: str


class _KeyMappingMeta(type):
    def __getattribute__(cls, name: str) -> KeyMapping:
        if (
            not name.startswith("_")
            and is_dataclass(cls)
            and name in [f.name for f in fields(cls)]
        ):
            return KeyMapping(name)
        return object.__getattribute__(cls, name)


@dataclass(frozen=True)
class KeyMappingConfig(metaclass=_KeyMappingMeta):
    left: KeyCode | tuple[KeyCode, ...] = (K_LEFT, K_a)
    right: KeyCode | tuple[KeyCode, ...] = (K_RIGHT, K_d)
    up: KeyCode | tuple[KeyCode, ...] = (K_UP, K_w)
    down: KeyCode | tuple[KeyCode, ...] = (K_DOWN, K_s)
    confirm: KeyCode | tuple[KeyCode, ...] = (K_RETURN, K_SPACE)
    cancel: KeyCode | tuple[KeyCode, ...] = (K_ESCAPE, K_TAB)
    full_screen_toggle: KeyCode | tuple[KeyCode, ...] = K_F1
    include_fps_in_title_toggle: KeyCode | tuple[KeyCode, ...] = K_F2
    debug_toggle: KeyCode | tuple[KeyCode, ...] = K_F3
