"""
Local entry point.
"""

from interior_scene import interior_scene
from nextrpg.game import Game

# set_config(Config(debug=DebugConfig()))
Game(interior_scene).start()
