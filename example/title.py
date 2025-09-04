from pathlib import Path

from example.interior_scene import interior_scene
from nextrpg import (
    BLUE,
    Button,
    Color,
    Label,
    Panel,
    PanelConfig,
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
        active=start_text_selected.drawing_group,
        on_click=scene,
    )

    load_text_idle = Text("Load")
    load_text_selected = load_text_idle.configured(highlight)
    load = Button(
        name="load",
        idle=load_text_idle.drawing_group,
        active=load_text_selected.drawing_group,
        on_click=load_panel(),
    )

    settings_text_idle = Text("Settings")
    settings_text_selected = settings_text_idle.configured(highlight)
    settings = Button(
        name="settings",
        idle=settings_text_idle.drawing_group,
        active=settings_text_selected.drawing_group,
        on_click=quit,
    )

    exit_text_idle = Text("Exit")
    exit_text_selected = exit_text_idle.configured(highlight)
    exit_button = Button(
        name="exit",
        idle=exit_text_idle.drawing_group,
        active=exit_text_selected.drawing_group,
        on_click=quit,
    )

    group = WidgetGroup(children=(start, load, settings, exit_button))

    tmx = Path("example/asset/title.tmx")
    return TitleScene(tmx_file=tmx, background="background", widget_input=group)


def load_panel() -> Panel:
    return Panel(
        name="load_panel",
        children=(Label(message="No save data found."),),
        config=PanelConfig(background=Color(0, 0, 0, 128)),
    )
