# /// script
# dependencies = ["nextrpg"]
# ///

from asyncio import run

from example.config import create_config
from example.scene.entry_scene import entry_scene
from nextrpg import Game

game = Game(entry_scene, create_config())
run(game.start_web())
