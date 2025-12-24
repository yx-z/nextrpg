# /// script
# dependencies = ["nextrpg"]
# ///

from asyncio import run

from example.game import GAME

run(GAME.start_web())
