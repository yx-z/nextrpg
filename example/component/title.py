from collections.abc import Callable
from functools import cache
from pathlib import Path

from example.scene.interior_scene import interior_scene
from nextrpg import (
    GREEN,
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
    Scene,
    ScrollDirection,
    Text,
    TimedAnimationOnScreens,
    TmxLoader,
    TmxWidgetGroupOnScreen,
    TransitionScene,
    Widget,
    WidgetGroup,
    animate,
    config,
    padding_for_all_sides,
    quit,
)
from nextrpg.animation.cycle import Cycle


def button(name: str, on_click: Scene | Widget | Callable[[], None]) -> Button:
    green = config().text.colored(GREEN)

    padding = padding_for_all_sides(10)
    background_color = Color(255, 255, 255, 150)
    text = Text(name.capitalize(), green)
    background = text.drawings[0].background(
        background_color, padding, border_radius=5
    )

    fade_in = FadeIn(background)
    fade_out = FadeOut(background)
    background_animations = Cycle((fade_in, fade_out))
    active = DrawingGroup((background_animations, text.drawing))
    return Button(
        name=name,
        active=active,
        idle=text.drawing,
        on_click=on_click,
    )


@cache
def title() -> TmxWidgetGroupOnScreen:
    scene = TransitionScene(interior_scene)
    start = button("start", scene)
    load = button("load", load_panel())
    options = button("options", quit)
    exit_button = button("exit", quit)

    group = WidgetGroup(
        children=(start, load, options, exit_button),
        scroll_direction=ScrollDirection.HORIZONTAL,
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
