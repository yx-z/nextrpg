"""
Local entry point.
"""

from interior_scene import interior_scene
from nextrpg.config import Config, DebugConfig, set_config
from nextrpg.game import Game

# set up global (debug) config
set_config(Config(debug=DebugConfig()))
Game(entry_scene=interior_scene).start()
