from pathlib import Path

from example.scene.interior_scene import interior_scene
from nextrpg import (
    GREEN,
    Button,
    Color,
    Direction,
    DirectionalOffset,
    DrawingOnScreen,
    FadeIn,
    Label,
    MoveTo,
    Panel,
    PanelConfig,
    ScrollDirection,
    Text,
    TmxWidgetGroupOnScreen,
    TransitionScene,
    WidgetGroup,
    config,
    quit,
)


def title() -> TmxWidgetGroupOnScreen:
    highlight = config().text.colored(GREEN)

    start_text_idle = Text("Start")
    start_text_selected = start_text_idle.configured(highlight)
    scene = TransitionScene(title, interior_scene)
    start = Button(
        name="start",
        idle=start_text_idle.drawing,
        active=start_text_selected.drawing,
        on_click=scene,
    )

    load_text_idle = Text("Load")
    load_text_selected = load_text_idle.configured(highlight)
    load = Button(
        name="load",
        idle=load_text_idle.drawing,
        active=load_text_selected.drawing,
        on_click=load_panel(),
    )

    options_text_idle = Text("Options")
    options_text_selected = options_text_idle.configured(highlight)
    options = Button(
        name="options",
        idle=options_text_idle.drawing,
        active=options_text_selected.drawing,
        on_click=quit,
    )

    exit_text_idle = Text("Exit")
    exit_text_selected = exit_text_idle.configured(highlight)
    exit_button = Button(
        name="exit",
        idle=exit_text_idle.drawing,
        active=exit_text_selected.drawing,
        on_click=quit,
    )

    children = (start, load, options, exit_button)
    group = WidgetGroup(
        children=children, scroll_direction=ScrollDirection.HORIZONTAL
    )

    tmx = Path("example/component/title.tmx")
    return TmxWidgetGroupOnScreen(
        tmx_file=tmx, background="background", widget=group
    )


def load_panel() -> Panel:
    child = Label(message="Loading...")
    children = (child,)
    background = Color(0, 0, 0, 128)
    panel_config = PanelConfig(background=background)
    return Panel(
        name="load_panel",
        children=children,
        config=panel_config,
        enter_animation=enter_panel,
    )


def enter_panel(drawing_on_screens: tuple[DrawingOnScreen, ...]) -> FadeIn:
    return MoveTo(
        resource=drawing_on_screens,
        offset=DirectionalOffset(Direction.DOWN, 50),
        duration=300,
    ).compose(FadeIn)
