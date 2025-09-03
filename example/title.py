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
        name="start",
        idle=start_text_idle.drawing_group,
        selected=start_text_selected.drawing_group,
        on_click=scene,
    )

    load_text_idle = Text("Load")
    load_text_selected = load_text_idle.configured(highlight)
    load = Button(
        name="load",
        idle=load_text_idle.drawing_group,
        selected=load_text_selected.drawing_group,
        on_click=load_panel(),
    )

    settings_text_idle = Text("Settings")
    settings_text_selected = settings_text_idle.configured(highlight)
    settings = Button(
        name="settings",
        idle=settings_text_idle.drawing_group,
        selected=settings_text_selected.drawing_group,
        on_click=quit,
    )

    exit_text_idle = Text("Exit")
    exit_text_selected = exit_text_idle.configured(highlight)
    exit_button = Button(
        name="exit",
        idle=exit_text_idle.drawing_group,
        selected=exit_text_selected.drawing_group,
        on_click=quit,
    )

    group = WidgetGroup(children=(start, load, settings, exit_button))

    tmx = Path("example/asset/title.tmx")
    return TitleScene(tmx, "background", group)


def load_panel() -> Panel:
    group = WidgetGroup(children=())
    return Panel(name="load_panel", group=group)
