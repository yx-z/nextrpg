# /// script
# dependencies = ["nextrpg"]
# ///

from asyncio import run

from interior_scene import interior_scene
from nextrpg import Game

run(Game(entry_scene=interior_scene).start_async())
