from example.component.menu import menu_widget, tmx
from nextrpg import Config, MenuConfig


def create_config() -> Config:
    menu = MenuConfig(menu_widget, tmx)
    return Config(menu=menu)
