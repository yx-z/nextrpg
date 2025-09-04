import sys
from pathlib import Path

sys.path.append(str((Path(__file__) / "../..").absolute()))

from title import title

from nextrpg import Game

Game(title).start()
