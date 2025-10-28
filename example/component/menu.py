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
    FadeIn,
    Height,
    MapScene,
    MenuScene,
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

PADDING_WIDTH = Width(10)
PADDING_HEIGHT = Height(10)


def save_slots(area: AreaOnScreen) -> tuple[Widget, ...]:
    return tuple(save_slot(area, i) for i in range(1, NUM_SAVE_SLOTS + 1))


def save_slot(area: AreaOnScreen, i: int) -> Button:
    height = area.height / NUM_SAVE_SLOTS - PADDING_HEIGHT * 2
    width = area.width - PADDING_WIDTH * 2
    size = width * height
    top_left = area.top_left + i * height
    center = top_left.as_top_left_of(size).center
    # text_drawing = TextOnScreen()
    return button(
        name=f"Save slot #{i}",
        coordinate=top_left,
        on_click=lambda: print(f"Save to slot {i}"),
    )


@cache
def widget_group() -> WidgetGroup:
    save_panel = Panel(
        name="save_panel",
        create_children=save_slots,
        enter_animation=enter_animation_with_fade,
        exit_animation=exit_animation,
    )
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


def enter_animation_with_fade(
    drawing_on_screens: tuple[DrawingOnScreen, ...],
) -> TimedAnimationOnScreens:
    fade_in = animate(drawing_on_screens, FadeIn)
    return fade_in.compose(MoveTo, offset=WIDGET_OFFSET)


def exit_animation(
    drawing_on_screens: tuple[DrawingOnScreen, ...],
) -> TimedAnimationOnScreens:
    return enter_animation_with_fade(drawing_on_screens).reverse
