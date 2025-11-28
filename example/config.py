from example.component.menu import menu_widget, tmx
from example.item.item import ITEM_CONFIG
from nextrpg import Config, MenuConfig


def create_config() -> Config:
    menu = MenuConfig(menu_widget, tmx)
    return Config(menu=menu, item=ITEM_CONFIG)
