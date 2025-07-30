import sys
from pathlib import Path

sys.path.append(str((Path(__file__) / "../..").absolute()))

from interior_scene import interior_scene

from nextrpg import Config, DebugConfig, Game, TextGroupConfig, set_config

set_config(Config(debug=DebugConfig()))
set_config(Config())
Game(entry_scene=interior_scene).start()
