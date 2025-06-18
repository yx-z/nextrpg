"""
Local entry point.
"""

from nextrpg.config import Config, DebugConfig, set_config
from nextrpg.game import Game
from sample_scene import entry_scene

set_config(Config(debug=DebugConfig()))
Game(entry_scene).start()
