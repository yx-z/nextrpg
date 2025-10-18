from functools import cache
from pathlib import Path

from example.component.title import title
from nextrpg import (
    BLUE,
    Button,
    Direction,
    DirectionalOffset,
    DrawingOnScreen,
    FadeIn,
    MapScene,
    MenuScene,
    MoveTo,
    ScrollDirection,
    Text,
    TimedAnimationOnScreens,
    TmxLoader,
    TransitionScene,
    WidgetGroup,
    animate,
    config,
)


def menu(map: MapScene) -> MenuScene:
    return MenuScene(map=map, widget=widget_group(), tmx=tmx())


@cache
def tmx() -> TmxLoader:
    tmx_path = Path("example/component/menu.tmx")
    return TmxLoader(tmx_path)


@cache
def widget_group() -> WidgetGroup:
    highlight = config().text.colored(BLUE)
    save_idle = Text("Save")
    save_selected = save_idle.configured(highlight)
    save_button = Button(
        name="save",
        idle=save_idle.drawing,
        active=save_selected.drawing,
        on_click=lambda: print("Save button clicked"),
    )

    title_idle = Text("Title")
    title_selected = title_idle.configured(highlight)
    title_scene = TransitionScene(title)
    title_button = Button(
        name="title",
        idle=title_idle.drawing,
        active=title_selected.drawing,
        on_click=title_scene,
    )

    widgets = (save_button, title_button)
    return WidgetGroup(
        children=widgets,
        scroll_direction=ScrollDirection.HORIZONTAL,
        enter_animation=enter_animation,
    )


def enter_animation(
    drawing_on_screens: tuple[DrawingOnScreen, ...],
) -> TimedAnimationOnScreens:
    offset = DirectionalOffset(Direction.DOWN, 50)
    move = animate(drawing_on_screens, MoveTo, offset=offset, duration=200)
    return move.compose(FadeIn)
