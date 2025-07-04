"""
Web entry point.

The import comments below are required for pygbag.
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

run(Game(entry_scene=interior_scene).start_async())
