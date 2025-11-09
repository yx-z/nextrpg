from dataclasses import dataclass, fields, is_dataclass
from typing import Self

from pygame import (
    K_DOWN,
    K_ESCAPE,
    K_F1,
    K_F2,
    K_F3,
    K_LEFT,
    K_RETURN,
    K_RIGHT,
    K_UP,
)

type KeyCode = int


@dataclass(frozen=True)
class KeyMapping:
    name: str

    @property
    def resolve(self) -> KeyCode:
        from nextrpg.config.config import config

        key_mappings = config().key_mapping
        return getattr(key_mappings, self.name)

    @classmethod
    def from_key(cls, key_code: KeyCode) -> Self | None:
        from nextrpg.config.config import config

        key_mappings = config().key_mapping
        for field in fields(key_mappings):
            if getattr(key_mappings, field.name) == key_code:
                return cls(field.name)
        return None


class _KeyMappingMeta(type):
    def __getattribute__(cls, name: str) -> KeyMapping:
        if name.startswith("_"):
            return object.__getattribute__(cls, name)

        if is_dataclass(cls) and name in [f.name for f in fields(cls)]:
            mapping = KeyMapping(name)
            return mapping
        return object.__getattribute__(cls, name)


@dataclass(frozen=True)
class KeyMappingConfig(metaclass=_KeyMappingMeta):
    left: KeyCode = K_LEFT
    right: KeyCode = K_RIGHT
    up: KeyCode = K_UP
    down: KeyCode = K_DOWN
    confirm: KeyCode = K_RETURN
    cancel: KeyCode = K_ESCAPE
    full_screen_toggle: KeyCode | None = K_F1
    include_fps_in_title_toggle: KeyCode | None = K_F2
    debug_toggle: KeyCode | None = K_F3
