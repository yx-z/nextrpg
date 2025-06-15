"""
Local entry point.
"""

from nextrpg.config import Config, DebugConfig, set_config
from nextrpg.start_game import start_game
from sample_scene import entry_scene

if __name__ == "__main__":
    set_config(Config(debug=DebugConfig()))
    set_config(Config())
    start_game(entry_scene)
