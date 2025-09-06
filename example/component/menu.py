from pathlib import Path

from example.component.title import title
from nextrpg import (
    BLUE,
    Button,
    DrawingOnScreens,
    MapScene,
    SaveIo,
    Text,
    TmxWidgets,
    WidgetGroup,
    config,
)


def menu(scene: MapScene) -> TmxWidgets:
    highlight = config().text.colored(BLUE)
    tmx = Path("example/component/menu.tmx")
    background = DrawingOnScreens(scene.drawing_on_screens).merge.blur(10)

    save_text_idle = Text("Save")
    save_text_selected = save_text_idle.configured(highlight)
    save = Button(
        name="save",
        idle=save_text_idle.drawing_group,
        selected=save_text_selected.drawing_group,
        on_click=lambda: SaveIo().save(scene),
    )

    title_text_idle = Text("Title")
    title_text_selected = title_text_idle.configured(highlight)
    title_button = Button(
        name="title",
        idle=title_text_idle.drawing_group,
        selected=title_text_selected.drawing_group,
        on_click=title(),
    )
    children = (save, title_button)
    group = WidgetGroup(children=children)
    return TmxWidgets(tmx=tmx, background=background, widget_input=group)
