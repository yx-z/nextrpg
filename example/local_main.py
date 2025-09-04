import sys
from pathlib import Path

sys.path.append(str((Path(__file__) / "../..").absolute()))

from title import create_title

from nextrpg import Config, DebugConfig, Game

Game(create_title, Config(debug=DebugConfig())).start()
