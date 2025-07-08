"""
Local entry point.
"""

import sys
from pathlib import Path

sys.path.append(str((Path(__file__) / "../..").absolute()))

from interior_scene import interior_scene
from nextrpg.config import Config, DebugConfig, set_config
from nextrpg.game import Game

# set up global (debug) config
set_config(Config(debug=DebugConfig()))
Game(entry_scene=interior_scene).start()
