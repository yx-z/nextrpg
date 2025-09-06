# /// script
# dependencies = ["nextrpg", "cachetools"]
# ///

from asyncio import run

from example.scene.interior_scene import interior_scene
from nextrpg import Game

run(Game(entry_scene=interior_scene).start_web())
