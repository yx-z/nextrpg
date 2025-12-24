import sys
from pathlib import Path

root = Path(__file__) / ".." / ".."
sys.path.append(str(root.resolve()))

from example.game import GAME

GAME.start()
