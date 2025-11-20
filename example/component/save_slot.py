from typing import Callable

from nextrpg import (
    BaseButton,
    Button,
    ButtonConfig,
    ButtonOnScreen,
    Direction,
    DirectionalOffset,
    FadeIn,
    GameSaveMeta,
    GameState,
    Height,
    MoveTo,
    OnClickResult,
    Panel,
    PanelOnScreen,
    SaveIo,
    Text,
    TimedAnimationSpec,
    Width,
)

NUM_SAVE_SLOTS = 3
PADDING_WIDTH = Width(10)
PADDING_HEIGHT = Height(10)

WIDGET_OFFSET = DirectionalOffset(Direction.DOWN, 50)
ENTER_ANIMATION = TimedAnimationSpec(FadeIn).compose(
    MoveTo, offset=WIDGET_OFFSET
)

PANEL_NAME = "panel"


def create_save_panel(
    click_save_slot: Callable[[int, ButtonOnScreen, GameState], OnClickResult],
) -> Callable[[ButtonOnScreen, GameState], PanelOnScreen]:
    def on_click(button: ButtonOnScreen, state: GameState) -> PanelOnScreen:
        save_slots = tuple(
            create_save_slot(i, click_save_slot) for i in range(NUM_SAVE_SLOTS)
        )
        panel = Panel(
            name=PANEL_NAME,
            children=save_slots,
            enter_animation=ENTER_ANIMATION,
        )
        assert button.parent, f"Button should have parent. Got {button}."
        return panel.with_parent(button.parent)

    return on_click


def create_save_slot(
    slot: int,
    click_save_slot: Callable[[int, ButtonOnScreen, GameState], OnClickResult],
) -> Callable[[PanelOnScreen], BaseButton]:
    def on_click(button: ButtonOnScreen, state: GameState) -> OnClickResult:
        return click_save_slot(slot, button, state)

    def create_button(panel: PanelOnScreen) -> Button:
        height = panel.area.height / NUM_SAVE_SLOTS - PADDING_HEIGHT
        width = panel.area.width - PADDING_WIDTH
        size = width * height
        config = ButtonConfig(padding_or_size=size)
        top_left = panel.area.top_left + height * slot

        save_io = SaveIo(str(slot))
        if game_save_meta := save_io.load(GameSaveMeta):
            title = f"Save #{slot + 1}: {game_save_meta.save_time_str}"
        else:
            title = f"Empty Save Slot #{slot + 1}"
        text = Text(title)

        button = Button(
            coordinate=top_left, text=text, on_click=on_click, config=config
        )
        return button.add_metadata(save_slot=slot)

    return create_button
