from functools import cache
from pathlib import Path

from example.component.button import button
from example.component.title import title
from nextrpg import (
    AreaOnScreen,
    Button,
    Direction,
    DirectionalOffset,
    DrawingOnScreen,
    FadeOut,
    Height,
    MapScene,
    MenuScene,
    MoveFrom,
    MoveTo,
    Panel,
    ScrollDirection,
    TimedAnimationOnScreens,
    TmxLoader,
    TransitionScene,
    Widget,
    WidgetGroup,
    Width,
    animate,
)


def menu(map: MapScene) -> MenuScene:
    return MenuScene(map=map, widget=widget_group(), tmx=tmx())


@cache
def tmx() -> TmxLoader:
    tmx_path = Path("example/component/menu.tmx")
    return TmxLoader(tmx_path)


NUM_SAVE_SLOTS = 3


def save_slots(area: AreaOnScreen) -> tuple[Widget, ...]:
    return tuple(save_slot(area, i) for i in range(NUM_SAVE_SLOTS))


def save_slot(area: AreaOnScreen, i: int) -> Button:
    PADDING_WIDTH = Width(10)
    PADDING_HEIGHT = Height(10)

    button_width = area.width - PADDING_WIDTH * 2
    button_height = area.height / NUM_SAVE_SLOTS
    button_size = button_width * button_height

    return button(
        name=f"Save #{i}",
        coordinate=area.top_left
        + PADDING_WIDTH
        + button_height * i
        + PADDING_HEIGHT * i,
        on_click=lambda: print(f"Save to slot {i + 1}"),
    )


@cache
def widget_group() -> WidgetGroup:
    save_panel = Panel(name="save_panel", create_children=save_slots)
    save_button = button("save", save_panel)

    title_scene = TransitionScene(title)
    title_button = button("title", title_scene)

    widgets = (save_button, title_button)
    return WidgetGroup(
        children=widgets,
        scroll_direction=ScrollDirection.HORIZONTAL,
        enter_animation=enter_animation,
        exit_animation=exit_animation,
    )


WIDGET_OFFSET = DirectionalOffset(Direction.DOWN, 50)


def enter_animation(
    drawing_on_screens: tuple[DrawingOnScreen, ...],
) -> TimedAnimationOnScreens:
    return animate(drawing_on_screens, MoveTo, offset=WIDGET_OFFSET)


def exit_animation(
    drawing_on_screens: tuple[DrawingOnScreen, ...],
) -> TimedAnimationOnScreens:
    fade_out = animate(drawing_on_screens, FadeOut)
    return fade_out.compose(MoveFrom, offset=-WIDGET_OFFSET)
