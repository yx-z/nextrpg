import sys
from pathlib import Path

sys.path.append(str((Path(__file__) / "../..").absolute()))

from exterior_scene import exterior_scene

from nextrpg import Config, DebugConfig, Game

Game(exterior_scene, Config(debug=DebugConfig())).start()
