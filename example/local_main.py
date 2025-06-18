"""
Local entry point.
"""

from nextrpg.config import Config, DebugConfig, set_config
from nextrpg.game import Game
from sample_scene import entry_scene

if __name__ == "__main__":
    set_config(Config(debug=DebugConfig()))
    # set_config(Config())
    Game.load(entry_scene).start()
