from pathlib import Path

from example.scene.interior_scene import interior_scene
from nextrpg import (
    BLUE,
    AnimationOnScreen,
    Button,
    Direction,
    DirectionalOffset,
    DrawingOnScreen,
    FadeIn,
    FadeOut,
    Label,
    MoveFrom,
    MoveTo,
    Panel,
    Text,
    TmxWidgets,
    TransitionScene,
    WidgetGroup,
    config,
    quit,
)


def title() -> TmxWidgets:
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

    children = (start, load, settings, exit_button)
    group = WidgetGroup(children=children)

    tmx = Path("example/component/title.tmx")
    return TmxWidgets(tmx=tmx, background="background", widget_input=group)


def load_panel() -> Panel:
    label = Label(message="No save data found.")
    children = (label,)
    return Panel(
        name="load_panel",
        children=children,
        entering_animation=entering_animation,
        exiting_animation=exiting_animation,
    )


duration = 300  # ms
offset = DirectionalOffset(Direction.DOWN, 50)


def entering_animation(
    drawing_on_screens: tuple[DrawingOnScreen, ...],
) -> AnimationOnScreen:
    return FadeIn(MoveTo(drawing_on_screens, offset, duration), duration)


def exiting_animation(
    drawing_on_screens: tuple[DrawingOnScreen, ...],
) -> AnimationOnScreen:
    return FadeOut(MoveFrom(drawing_on_screens, -offset, duration), duration)
