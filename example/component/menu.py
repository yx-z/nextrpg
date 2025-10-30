from functools import cache
from pathlib import Path

from example.component.title import title
from nextrpg import (
    TRANSPARENT,
    Anchor,
    AreaOnScreen,
    Button,
    ButtonConfig,
    DefaultButton,
    Direction,
    DirectionalOffset,
    DrawingOnScreen,
    DrawingOnScreens,
    FadeIn,
    Height,
    MapScene,
    MenuScene,
    MoveTo,
    Panel,
    ScrollDirection,
    Text,
    TextOnScreen,
    TimedAnimationOnScreens,
    TmxLoader,
    TransitionScene,
    Widget,
    WidgetGroup,
    Width,
    animate,
)
from nextrpg.geometry.padding import Padding


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
    return tuple(save_slot(area, i) for i in range(NUM_SAVE_SLOTS))


def save_slot(area: AreaOnScreen, i: int) -> Button:
    height = area.height / NUM_SAVE_SLOTS - PADDING_HEIGHT * 2
    width = area.width - PADDING_WIDTH * 2
    top_left = area.top_left + i * height + PADDING_HEIGHT + PADDING_WIDTH
    button = top_left.as_top_left_of(width * height)

    background = button.rectangle_area_on_screen.fill(TRANSPARENT)
    text = Text(f"Save #{i}")
    text_on_screen = TextOnScreen(button.center, text, Anchor.CENTER)
    drawing_on_screens = DrawingOnScreens(
        (background, text_on_screen.drawing_on_screen)
    )
    return DefaultButton(
        text=drawing_on_screens.drawing_group_at_origin,
        coordinate=top_left,
        on_click=lambda: print(f"Save to slot {i}"),
        config=ButtonConfig(padding=Padding()),
    )


@cache
def widget_group() -> WidgetGroup:
    save_panel = Panel(
        name="save_panel",
        create_children=save_slots,
        enter_animation=enter_animation_with_fade,
        exit_animation=exit_animation,
    )
    save_button = DefaultButton(name="save", on_click=save_panel)

    title_scene = TransitionScene(title)
    title_button = DefaultButton(name="title", on_click=title_scene)

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
