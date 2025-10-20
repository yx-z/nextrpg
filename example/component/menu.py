from functools import cache
from pathlib import Path

from example.component.title import button, title
from nextrpg import (
    Direction,
    DirectionalOffset,
    DrawingOnScreen,
    FadeIn,
    MapScene,
    MenuScene,
    MoveTo,
    ScrollDirection,
    TimedAnimationOnScreens,
    TmxLoader,
    TransitionScene,
    WidgetGroup,
    animate,
)


def menu(map: MapScene) -> MenuScene:
    return MenuScene(map=map, widget=widget_group(), tmx=tmx())


@cache
def tmx() -> TmxLoader:
    tmx_path = Path("example/component/menu.tmx")
    return TmxLoader(tmx_path)


@cache
def widget_group() -> WidgetGroup:
    save_button = button("save", lambda: print("Saved!"))
    title_scene = TransitionScene(title)
    title_button = button("title", title_scene)

    widgets = (save_button, title_button)
    return WidgetGroup(
        children=widgets,
        scroll_direction=ScrollDirection.HORIZONTAL,
        enter_animation=enter_animation,
    )


def enter_animation(
    drawing_on_screens: tuple[DrawingOnScreen, ...],
) -> TimedAnimationOnScreens:
    fade_in = animate(drawing_on_screens, FadeIn)
    offset = DirectionalOffset(Direction.DOWN, 50)
    return fade_in.compose(MoveTo, offset=offset)
