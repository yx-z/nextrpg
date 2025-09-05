import sys
from pathlib import Path

sys.path.append(str((Path(__file__) / "../..").absolute()))
from title import title

from nextrpg import Config, DebugConfig, Game

Game(title, Config(debug=DebugConfig())).start()
