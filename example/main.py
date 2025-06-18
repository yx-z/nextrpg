"""
Web entry point.
"""

# /// script
# dependencies = [
#   "nextrpg",
#   "pytmx",
# ]
# ///

from nextrpg.game import Game
from sample_scene import entry_scene

Game.load(entry_scene).start_async()
