import sys
from pathlib import Path

sys.path.append(str((Path(__file__) / "../..").absolute()))

from interior_scene import interior_scene

from nextrpg import LOG_ONLY, Config, DebugConfig, Game

Game(interior_scene, Config(debug=DebugConfig())).start()
