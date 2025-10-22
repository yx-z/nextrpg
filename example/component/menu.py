from functools import cache
from pathlib import Path

from example.component.title import button, title
from nextrpg import (
    Direction,
    DirectionalOffset,
    DrawingOnScreen,
    FadeOut,
    Log,
    MapScene,
    MenuScene,
    MoveFrom,
    MoveTo,
    ScrollDirection,
    TimedAnimationOnScreens,
    TmxLoader,
    TransitionScene,
    WidgetGroup,
    animate,
)

log = Log()


def menu(map: MapScene) -> MenuScene:
    return MenuScene(map=map, widget=widget_group(), tmx=tmx())


@cache
def tmx() -> TmxLoader:
    tmx_path = Path("example/component/menu.tmx")
    return TmxLoader(tmx_path)


@cache
def widget_group() -> WidgetGroup:
    save_button = button("save", lambda: print("Saved!"))
    log.debug_drawing(save_button=save_button.active)
    title_scene = TransitionScene(title)
    title_button = button("title", title_scene)

    widgets = (save_button, title_button)
    return WidgetGroup(
        children=widgets,
        scroll_direction=ScrollDirection.HORIZONTAL,
        enter_animation=enter_animation,
        exit_animation=exit_animation,
    )


offset = DirectionalOffset(Direction.DOWN, 50)


def enter_animation(
    drawing_on_screens: tuple[DrawingOnScreen, ...],
) -> TimedAnimationOnScreens:
    return animate(drawing_on_screens, MoveTo, offset=offset)


def exit_animation(
    drawing_on_screens: tuple[DrawingOnScreen, ...],
) -> TimedAnimationOnScreens:
    fade_out = animate(drawing_on_screens, FadeOut)
    return fade_out.compose(MoveFrom, offset=-offset)
