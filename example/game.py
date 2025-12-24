from example.component.menu import MENU_CONFIG
from example.component.title import title
from example.item.item import ITEM_CONFIG
from nextrpg import (
    Config,
    DrawingConfig,
    Font,
    Game,
    Height,
    RpgConfig,
    TextConfig,
)

TEXT_CONFIG = TextConfig(font=Font(Height(20), "Microsoft JhengHei", bold=True))
DRAWING_CONFIG = DrawingConfig(text=TEXT_CONFIG)
RPG_CONFIG = RpgConfig(item=ITEM_CONFIG)
CONFIG = Config(menu=MENU_CONFIG, rpg=RPG_CONFIG, drawing=DRAWING_CONFIG)
GAME = Game(title, config=CONFIG)
