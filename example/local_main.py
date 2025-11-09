import sys
from pathlib import Path

from example.config import create_config
from example.scene.entry_scene import entry_scene

root = Path(__file__) / ".." / ".."
root_str = str(root.resolve())
sys.path.append(root_str)

from nextrpg import Game

Game(entry_scene, create_config()).start()
