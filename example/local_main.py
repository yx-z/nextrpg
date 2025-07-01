"""
Local entry point.
"""

from interior_scene import interior_scene
from nextrpg.config import (
    Config,
    DebugConfig,
    GuiConfig,
    ResizeMode,
    set_config,
)
from nextrpg.game import Game

set_config(
    Config(
        GuiConfig(resize_mode=ResizeMode.KEEP_NATIVE_SIZE), debug=DebugConfig()
    )
)
Game(interior_scene).start()
