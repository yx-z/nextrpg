import sys
from pathlib import Path

sys.path.append(str((Path(__file__) / "../..").absolute()))

from interior_scene import interior_scene

from nextrpg import LOG_ONLY, Config, Game

Game(interior_scene, Config(debug=LOG_ONLY)).start()
