from typing import Callable

from nextrpg import (
    TRANSPARENT,
    Anchor,
    Button,
    ButtonConfig,
    ButtonOnScreen,
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
    Scene,
    Text,
    TextOnScreen,
    TimedAnimationSpec,
    WidgetOnScreen,
    Width,
    load_save_meta,
)

NUM_SAVE_SLOTS = 3
PADDING_WIDTH = Width(10)
PADDING_HEIGHT = Height(10)

WIDGET_OFFSET = DirectionalOffset(Direction.DOWN, 50)
ENTER_ANIMATION = TimedAnimationSpec(FadeIn).compose(
    MoveTo, offset=WIDGET_OFFSET
)


def create_save_panel(
    name: str,
    click_save_slot: Callable[
        [int], Callable[[ButtonOnScreen], WidgetOnScreen | Scene | None]
    ],
) -> Callable[[ButtonOnScreen], PanelOnScreen]:
    def on_click(button: ButtonOnScreen) -> PanelOnScreen:
        save_slots = [
            create_save_slot(i, click_save_slot) for i in range(NUM_SAVE_SLOTS)
        ]
        panel = Panel(
            name=name, children=save_slots, enter_animation=ENTER_ANIMATION
        )
        assert button.parent, f"Button should have parent. Got {button}."
        return panel.with_parent(button.parent)

    return on_click


def create_save_slot(
    i: int,
    click_save_slot: Callable[
        [int], Callable[[ButtonOnScreen], WidgetOnScreen | Scene | None]
    ],
) -> Callable[[PanelOnScreen], Button]:
    def create_button(panel: PanelOnScreen) -> DefaultButton:
        area = panel.area
        height = area.height / NUM_SAVE_SLOTS - PADDING_HEIGHT * 2
        width = area.width - PADDING_WIDTH * 2
        top_left = area.top_left + i * height + PADDING_HEIGHT + PADDING_WIDTH
        button = top_left.as_top_left_of(width * height)

        # To keep button size stable between idle and active.
        invisible_background = button.rectangle_area_on_screen.fill(TRANSPARENT)

        if game_save_meta := load_save_meta(str(i)):
            save_slot_title = f"Save #{i + 1}: {game_save_meta.save_time_str}"
        else:
            save_slot_title = f"Empty Save Slot #{i + 1}"
        text = Text(save_slot_title)
        text_on_screen = TextOnScreen(button.center, text, Anchor.CENTER)
        drawing_on_screens = DrawingOnScreens(
            (invisible_background, text_on_screen.drawing_on_screen)
        )
        click = click_save_slot(i)

        config = ButtonConfig(padding=Padding())
        button = DefaultButton(
            text=drawing_on_screens.drawing_group_at_origin,
            coordinate=top_left,
            on_click=click,
            config=config,
        )
        return button.add_metadata(save_slot=i)

    return create_button
