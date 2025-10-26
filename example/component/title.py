from functools import cache
from pathlib import Path

from example.component.button import button
from example.scene.interior_scene import interior_scene
from nextrpg import (
    Direction,
    DirectionalOffset,
    DrawingOnScreen,
    FadeIn,
    MoveTo,
    ScrollDirection,
    TimedAnimationOnScreens,
    TmxLoader,
    TmxWidgetGroupOnScreen,
    TransitionScene,
    WidgetGroup,
    animate,
    quit,
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
