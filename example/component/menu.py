from collections.abc import Callable
from functools import cache
from pathlib import Path

from example.component.title import title
from nextrpg import (
    TRANSPARENT,
    Anchor,
    Button,
    ButtonConfig,
    DefaultButton,
    Direction,
    DirectionalOffset,
    DrawingOnScreens,
    FadeIn,
    Height,
    MoveTo,
    Padding,
    Panel,
    PanelOnScreen,
    ScrollDirection,
    Text,
    TextOnScreen,
    TimedAnimationSpec,
    TmxLoader,
    TransitionScene,
    WidgetGroup,
    Width,
)


@cache
def tmx() -> TmxLoader:
    tmx_path = Path("example/component/menu.tmx")
    return TmxLoader(tmx_path)


NUM_SAVE_SLOTS = 3


@cache
def menu_widget() -> WidgetGroup:
    WIDGET_OFFSET = DirectionalOffset(Direction.DOWN, 50)
    enter_animation = TimedAnimationSpec(FadeIn).compose(
        MoveTo, offset=WIDGET_OFFSET
    )
    save_slots = tuple(save_slot(i) for i in range(NUM_SAVE_SLOTS))
    save_panel = Panel(
        name="save_panel",
        children=save_slots,
        enter_animation=enter_animation,
    )
    save_button = DefaultButton(name="save", on_click=save_panel)

    title_scene = TransitionScene(title)
    title_button = DefaultButton(name="title", on_click=title_scene)

    widgets = (save_button, title_button)
    return WidgetGroup(
        children=widgets,
        scroll_direction=ScrollDirection.HORIZONTAL,
        enter_animation=enter_animation,
    )


def save_slot(i: int) -> Callable[[PanelOnScreen], Button]:
    PADDING_WIDTH = Width(10)
    PADDING_HEIGHT = Height(10)

    def create_button(panel: PanelOnScreen) -> Button:
        area = panel.area
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

    return create_button
