from pathlib import Path

from example.component.title import title
from nextrpg import (
    BLUE,
    Button,
    MapScene,
    MenuScene,
    ScrollDirection,
    Text,
    TmxLoader,
    TmxWidgetGroupOnScreen,
    TransitionScene,
    WidgetGroup,
    config,
)


def menu(map: MapScene) -> MenuScene:
    tmx = tmx_widget_group_on_screen(map)
    return MenuScene(map, tmx)


def tmx_widget_group_on_screen(map: MapScene) -> TmxWidgetGroupOnScreen:
    tmx_path = Path("example/component/menu.tmx")
    tmx = TmxLoader(tmx_path)

    highlight = config().text.colored(BLUE)
    save_idle = Text("Save")
    save_selected = save_idle.configured(highlight)
    save_button = Button(
        name="save",
        idle=save_idle.drawing,
        active=save_selected.drawing,
        on_click=lambda: print("Save button clicked"),
    )

    title_idle = Text("Title")
    title_selected = title_idle.configured(highlight)

    def from_scene() -> MenuScene:
        return menu(map).fade_in_complete

    title_scene = TransitionScene(from_scene, title)
    title_button = Button(
        name="title",
        idle=title_idle.drawing,
        active=title_selected.drawing,
        on_click=title_scene,
    )

    widgets = (save_button, title_button)
    widget_group = WidgetGroup(
        children=widgets, scroll_direction=ScrollDirection.HORIZONTAL
    )
    return TmxWidgetGroupOnScreen(tmx=tmx, background=(), widget=widget_group)
