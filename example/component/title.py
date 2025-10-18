from functools import cache
from pathlib import Path

from example.scene.interior_scene import interior_scene
from nextrpg import (
    GREEN,
    WHITE,
    Button,
    Color,
    Direction,
    DirectionalOffset,
    DrawingGroup,
    DrawingOnScreen,
    FadeIn,
    FadeOut,
    Label,
    MoveTo,
    Panel,
    PanelConfig,
    ScrollDirection,
    Sequence,
    Text,
    TimedAnimationOnScreens,
    TmxLoader,
    TmxWidgetGroupOnScreen,
    TransitionScene,
    WidgetGroup,
    animate,
    config,
    quit,
)
from nextrpg.animation.cycle import Cycle


@cache
def title() -> TmxWidgetGroupOnScreen:
    highlight = config().text.colored(GREEN)

    start_text = Text("Start").configured(highlight)
    start_text_background = start_text.drawings[0].background(WHITE).no_shift
    background_animation = Cycle(
        Sequence(
            (
                FadeOut(start_text_background).no_shift,
                FadeIn(start_text_background).no_shift,
            )
        ).no_shift
    )
    start_text_active = DrawingGroup(
        (background_animation.no_shift, start_text.drawing.no_shift)
    )
    scene = TransitionScene(interior_scene)
    start = Button(
        name="start",
        idle=start_text.drawing,
        active=start_text_active,
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

    tmx_path = Path("example/component/title.tmx")
    tmx_loader = TmxLoader(tmx_path)
    return TmxWidgetGroupOnScreen(
        tmx=tmx_loader, background="background", widget=group
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


def enter_panel(
    drawing_on_screens: tuple[DrawingOnScreen, ...],
) -> TimedAnimationOnScreens:
    offset = DirectionalOffset(Direction.DOWN, 50)
    move = animate(drawing_on_screens, MoveTo, offset=offset, duration=300)
    return move.compose(FadeIn)
