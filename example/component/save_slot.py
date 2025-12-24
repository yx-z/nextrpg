from pathlib import Path
from typing import Callable

from nextrpg import (
    AddChildWidget,
    Button,
    ButtonConfig,
    ButtonSpec,
    FadeIn,
    GameSaveMeta,
    GameState,
    MoveTo,
    PanelSpec,
    SaveIo,
    Size,
    TimedAnimationSpec,
    WidgetInteractionResult,
)

TMX_DIR = Path(__file__).parent / "tmx"
ENTER_ANIMATION = TimedAnimationSpec(FadeIn).compose(MoveTo, offset=Size(0, 50))


def create_save_panel(
    click_save_slot: Callable[
        [Button, GameState, str], WidgetInteractionResult
    ],
) -> Callable[[Button, GameState], AddChildWidget]:
    def on_click(button: Button, state: GameState) -> AddChildWidget:
        return AddChildWidget(
            PanelSpec(
                name="panel",
                enter_animation=ENTER_ANIMATION,
                loop=False,
                widgets=tuple(
                    create_save_slot(str(slot), click_save_slot)
                    for slot in range(10)
                ),
            )
        )

    return on_click


def create_save_slot(
    slot: str,
    click_save_slot: Callable[
        [Button, GameState, str], WidgetInteractionResult
    ],
) -> ButtonSpec:
    return ButtonSpec(
        text=(
            f"Save #{slot}: {meta.save_time_str}"
            if (meta := SaveIo(slot).load(GameSaveMeta))
            else f"Empty Save Slot #{slot}"
        ),
        on_click=lambda btn, state: click_save_slot(btn, state, slot),
        config=ButtonConfig(Size(400, 100)),
        metadata=(("slot", slot),),
    )
