from pathlib import Path

from example.interior_scene import interior_scene
from nextrpg import (
    BLUE,
    Button,
    Panel,
    Text,
    TitleScene,
    TransitionScene,
    WidgetGroup,
    config,
    quit,
)


def title() -> TitleScene:
    highlight = config().text.colored(BLUE)

    start_text_idle = Text("Start")
    start_text_selected = start_text_idle.configured(highlight)
    scene = TransitionScene(title, interior_scene)
    start = Button(
        "start",
        start_text_idle.drawing_group,
        start_text_selected.drawing_group,
        scene,
    )

    load_text_idle = Text("Load")
    load_text_selected = load_text_idle.configured(highlight)
    load = Button(
        "load",
        load_text_idle.drawing_group,
        load_text_selected.drawing_group,
        load_panel(),
    )

    settings_text_idle = Text("Settings")
    settings_text_selected = settings_text_idle.configured(highlight)
    settings = Button(
        "settings",
        settings_text_idle.drawing_group,
        settings_text_selected.drawing_group,
        quit,
    )

    exit_text_idle = Text("Exit")
    exit_text_selected = exit_text_idle.configured(highlight)
    exit_button = Button(
        "exit",
        exit_text_idle.drawing_group,
        exit_text_selected.drawing_group,
        quit,
    )

    group = WidgetGroup((start, load, settings, exit_button))

    tmx = Path("example/asset/title.tmx")
    return TitleScene(tmx, "background", group)


def load_panel() -> Panel:
    group = WidgetGroup(children=())
    return Panel("load_panel", group)
