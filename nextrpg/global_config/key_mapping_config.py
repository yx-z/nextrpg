from dataclasses import dataclass

from pygame import K_RETURN
from pygame.locals import K_DOWN, K_F1, K_LEFT, K_RIGHT, K_UP

type KeyCode = int


@dataclass(frozen=True)
class KeyMappingConfig:
    left: KeyCode = K_LEFT
    right: KeyCode = K_RIGHT
    up: KeyCode = K_UP
    down: KeyCode = K_DOWN
    confirm: KeyCode = K_RETURN
    gui_mode_toggle: KeyCode | None = K_F1
