from pathlib import Path

from example.interior_scene import interior_scene
from nextrpg import (
    BLUE,
    Button,
    SelectableWidgetGroup,
    Text,
    TitleScene,
    TransitionScene,
    config,
    quit,
)


def title() -> TitleScene:
    highlight = config().text.colored(BLUE)

    start_text_idle = Text("Start")
    start_text_selected = start_text_idle.configured(highlight)
    scene = TransitionScene(title, interior_scene)
    start = Button(
        unique_name="start",
        idle=start_text_idle.drawing_group,
        selected=start_text_selected.drawing_group,
        confirm=scene,
    )

    load_text_idle = Text("Load")
    load_text_selected = load_text_idle.configured(highlight)
    load = Button(
        unique_name="load",
        idle=load_text_idle.drawing_group,
        selected=load_text_selected.drawing_group,
        confirm=quit,
    )

    settings_text_idle = Text("Settings")
    settings_text_selected = settings_text_idle.configured(highlight)
    settings = Button(
        unique_name="settings",
        idle=settings_text_idle.drawing_group,
        selected=settings_text_selected.drawing_group,
        confirm=quit,
    )

    exit_text_idle = Text("Exit")
    exit_text_selected = exit_text_idle.configured(highlight)
    exit_button = Button(
        unique_name="exit",
        idle=exit_text_idle.drawing_group,
        selected=exit_text_selected.drawing_group,
        confirm=quit,
    )

    widgets = (start, load, settings, exit_button)
    group = SelectableWidgetGroup(widgets=widgets)

    tmx = Path("example/asset/title.tmx")
    return TitleScene(tmx, "background", group)
