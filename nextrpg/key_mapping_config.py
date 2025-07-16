"""
Key mapping configuration system for `nextrpg`.

This module provides configuration options for keyboard key mappings in `nextrpg`
games. It includes the `KeyMappingConfig` class for mapping game actions to
keyboard keys.

Features:
    - Type alias for key codes
    - Configurable key mappings for movement and actions
    - Integration with input handling system
"""

from dataclasses import dataclass

from pygame import K_RETURN
from pygame.locals import K_DOWN, K_F1, K_LEFT, K_RIGHT, K_UP

from nextrpg.model import export

type KeyCode = int
"""
Type alias for keyboard key codes used in pygame.

This type alias represents integer constants that identify specific keys on the
keyboard (like K_LEFT, K_RIGHT, etc.) as defined by pygame. These codes are used
in key mapping configurations and event handling.
"""


@export
@dataclass(frozen=True)
class KeyMappingConfig:
    """
    Configuration class for keyboard key mappings.

    This class defines the mapping between game actions and keyboard keys. Used
    by `nextrpg.event.pygame_event.KeyboardKey`, and the input handling system to
    translate keyboard input into game actions.

    Attributes:
        left: Key code for moving left. The default is `K_LEFT`.
        right: Key code for moving right. The default is `K_RIGHT`.
        up: Key code for moving up. The default is `K_UP`.
        down: Key code for moving down. The default is `K_DOWN`.
        confirm: Key code for confirming actions. The default is `K_SPACE`.
        gui_mode_toggle: Key code for toggling between windowed and full screen
            mode. The default is `F1`.
    """

    left: KeyCode = K_LEFT
    right: KeyCode = K_RIGHT
    up: KeyCode = K_UP
    down: KeyCode = K_DOWN
    confirm: KeyCode = K_RETURN
    gui_mode_toggle: KeyCode | None = K_F1
