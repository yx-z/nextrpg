from typing import Callable

from nextrpg import (
    Button,
    ButtonConfig,
    ButtonOnScreen,
    FadeIn,
    GameSaveMeta,
    GameState,
    Height,
    MoveTo,
    OnClickResult,
    Panel,
    PanelOnScreen,
    SaveIo,
    Size,
    Text,
    TimedAnimationSpec,
    Width,
)

NUM_SAVE_SLOTS = 3
PADDING_WIDTH = Width(10)
PADDING_HEIGHT = Height(10)

WIDGET_OFFSET = Size(0, 50)
ENTER_ANIMATION = TimedAnimationSpec(FadeIn).compose(
    MoveTo, offset=WIDGET_OFFSET
)

PANEL_NAME = "panel"


def create_save_panel(
    click_save_slot: Callable[[ButtonOnScreen, GameState, int], OnClickResult],
) -> Callable[[ButtonOnScreen, GameState], PanelOnScreen]:
    def on_click(button: ButtonOnScreen, state: GameState) -> PanelOnScreen:
        children = create_save_slots(click_save_slot)
        panel = Panel(
            name=PANEL_NAME, children=children, enter_animation=ENTER_ANIMATION
        )
        return panel.with_same_parent_as(button)

    return on_click


def create_save_slot(
    slot: int,
    click_save_slot: Callable[[ButtonOnScreen, GameState, int], OnClickResult],
) -> Button:
    save_io = SaveIo(str(slot))
    if game_save_meta := save_io.load(GameSaveMeta):
        title = f"Save #{slot + 1}: {game_save_meta.save_time_str}"
    else:
        title = f"Empty Save Slot #{slot}"
    text = Text(title)

    def on_click(btn: ButtonOnScreen, state: GameState) -> OnClickResult:
        return click_save_slot(btn, state, slot)

    size = Size(200, 100)
    config = ButtonConfig(padding_or_size=size)
    metadata = (("slot", slot),)
    return Button(
        text=text, on_click=on_click, config=config, metadata=metadata
    )


def create_save_slots(
    click_save_slot: Callable[[ButtonOnScreen, GameState, int], OnClickResult],
) -> tuple[Button, ...]:
    return tuple(
        create_save_slot(slot, click_save_slot)
        for slot in range(NUM_SAVE_SLOTS)
    )
