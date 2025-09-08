from pathlib import Path

from example.scene.interior_scene import interior_scene
from nextrpg import (
    GREEN,
    Button,
    Color,
    Direction,
    DirectionalOffset,
    FadeIn,
    FadeOut,
    Label,
    MoveFrom,
    MoveTo,
    Panel,
    PanelConfig,
    ScrollDirection,
    Text,
    TitleScene,
    TransitionScene,
    WidgetGroup,
    config,
    quit,
)


def title() -> TitleScene:
    highlight = config().text.colored(GREEN)

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

    options_text_idle = Text("Options")
    options_text_selected = options_text_idle.configured(highlight)
    options = Button(
        name="options",
        idle=options_text_idle.drawing_group,
        active=options_text_selected.drawing_group,
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

    children = (start, load, options, exit_button)
    group = WidgetGroup(
        children=children, scroll_direction=ScrollDirection.HORIZONTAL
    )

    tmx = Path("example/component/title.tmx")
    return TitleScene(tmx_file=tmx, background="background", widget_input=group)


def load_panel() -> Panel:
    offset = DirectionalOffset(Direction.DOWN, 50)
    duration = 300  # ms
    return Panel(
        name="load_panel",
        children=(Label(message="No save data found."),),
        config=PanelConfig(background=Color(0, 0, 0, 128)),
        entering_animation=lambda d: FadeIn(
            MoveTo(d, offset, duration), duration
        ),
        exiting_animation=lambda d: FadeOut(
            MoveFrom(d, -offset, duration), duration
        ),
    )
