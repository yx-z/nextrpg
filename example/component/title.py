from functools import cache
from pathlib import Path

from example.scene.interior_scene import interior_scene
from nextrpg import (
    DefaultButton,
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
    start = DefaultButton(name="start", on_click=scene)
    load = DefaultButton(name="load", on_click=lambda: None)
    options = DefaultButton(name="options", on_click=quit)
    exit_button = DefaultButton(name="exit", on_click=quit)

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
