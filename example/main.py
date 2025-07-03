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

from interior_scene import interior_scene
from nextrpg.game import Game

run(Game(interior_scene).start_async())