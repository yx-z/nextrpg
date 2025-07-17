"""
Local entry point.
"""

import sys
from pathlib import Path

sys.path.append(str((Path(__file__) / "../..").absolute()))

from interior_scene import interior_scene
from nextrpg import Game, Config, set_config, DebugConfig

# set up global (debug) global_config
set_config(Config(debug=DebugConfig()))
Game(entry_scene=interior_scene).start()
