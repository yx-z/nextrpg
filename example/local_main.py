"""
Local entry point.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1].resolve()))

from interior_scene import interior_scene
from nextrpg.game import Game

Game(interior_scene).start()
