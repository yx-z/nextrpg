import sys
from pathlib import Path

sys.path.append(str((Path(__file__) / "../..").resolve()))
from example.component.title import title
from nextrpg import Config, DebugConfig, Game

Game(title).start()
Game(title, config=Config(debug=DebugConfig())).start()
