import sys
from pathlib import Path

sys.path.append(str((Path(__file__) / "../..").resolve()))
from example.component.menu import menu
from example.component.title import title
from nextrpg import Config, DebugConfig, Game, MenuConfig

menu_config = MenuConfig(create=menu)
debug_config = DebugConfig()
# debug_config = None
config = Config(menu=menu_config, debug=debug_config)
Game(title, config=config).start()
