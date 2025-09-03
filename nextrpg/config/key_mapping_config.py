from dataclasses import dataclass

from pygame.locals import (
    K_DOWN,
    K_ESCAPE,
    K_F1,
    K_F2,
    K_LEFT,
    K_RETURN,
    K_RIGHT,
    K_UP,
)

type KeyCode = int


@dataclass(frozen=True)
class KeyMappingConfig:
    left: KeyCode = K_LEFT
    right: KeyCode = K_RIGHT
    up: KeyCode = K_UP
    down: KeyCode = K_DOWN
    confirm: KeyCode = K_RETURN
    cancel: KeyCode = K_ESCAPE
    full_screen_toggle: KeyCode | None = K_F1
    include_fps_in_title_toggle: KeyCode | None = K_F2
