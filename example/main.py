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

from nextrpg.start_game import async_start_game
from sample_scene import entry_scene

run(async_start_game(entry_scene))
