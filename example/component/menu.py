from functools import cache
from pathlib import Path

from nextrpg import MapScene, MenuScene, TmxLoader, TmxWidgetGroupOnScreen


def menu(map: MapScene) -> MenuScene:
    tmx = tmx_widget_group_on_screen()
    return MenuScene(map, tmx)


@cache
def tmx_widget_group_on_screen() -> TmxWidgetGroupOnScreen:
    tmx_path = Path("example/component/menu.tmx")
    tmx = TmxLoader(tmx_path)
    # TODO: Add widgets.
    return TmxWidgetGroupOnScreen(tmx=tmx, background=())
