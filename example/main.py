"""
Web entry point.
"""

# /// script
# dependencies = [
#   "nextrpg",
#   "pytmx",
# ]
# ///

from asyncio import run

from nextrpg.game import Game
from sample_scene import entry_scene

run(Game(entry_scene).start_async())
