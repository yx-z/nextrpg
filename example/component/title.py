from collections.abc import Callable
from functools import cache
from pathlib import Path

from example.scene.interior_scene import interior_scene
from nextrpg import (
    GREEN,
    WHITE,
    Button,
    Cycle,
    Direction,
    DirectionalOffset,
    DrawingGroup,
    DrawingOnScreen,
    FadeIn,
    FadeOut,
    MoveTo,
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


def button(name: str, on_click: Scene | Widget | Callable[[], None]) -> Button:
    green = config().text.colored(GREEN)

    padding = padding_for_all_sides(10)
    text = Text(name.capitalize(), green)
    border = text.drawings[0].background(
        WHITE, padding, width=1, border_radius=5
    )
    white = WHITE.percentage_alpha(0.7)
    background = text.drawings[0].background(white, padding, border_radius=5)

    fade_in = FadeIn((border, background))
    fade_out = FadeOut((border, background))
    animation = Cycle((fade_in, fade_out))
    active = DrawingGroup((animation, text.drawing))
    return Button(
        name=name, active=active, idle=text.drawing, on_click=on_click
    )


@cache
def title() -> TmxWidgetGroupOnScreen:
    scene = TransitionScene(interior_scene)
    start = button("start", scene)
    load = button("load", lambda: None)
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


def enter_panel(
    drawing_on_screens: tuple[DrawingOnScreen, ...],
) -> TimedAnimationOnScreens:
    offset = DirectionalOffset(Direction.DOWN, 50)
    move = animate(drawing_on_screens, MoveTo, offset=offset, duration=300)
    return move.compose(FadeIn)
