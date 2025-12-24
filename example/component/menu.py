from example.component.save_slot import (
    ENTER_ANIMATION,
    TMX_DIR,
    create_save_panel,
    create_save_slot,
)
from example.component.title import title
from example.scene.character import create_player_placeholder
from nextrpg import (
    Button,
    ButtonSpec,
    GameSave,
    GameState,
    MapScene,
    MenuConfig,
    PanelSpec,
    SaveIo,
    ScrollDirection,
    TransitionScene,
    WidgetLoader,
    stop_music,
)
from nextrpg.event.user_event import post_user_event
from nextrpg.widget.widget_interaction_result import ReplaceByWidget


def title_scene(button: Button, state: GameState) -> TransitionScene:
    stop_music()
    return TransitionScene(title)


def click_save_slot(from_button: Button, state: GameState, slot: str) -> None:
    root = from_button.root
    assert isinstance(
        root, MapScene
    ), f"Expect {from_button} called from a MapScene. Got {root}."
    game_save = GameSave(create_player_placeholder, state, root)

    SaveIo(slot).save(game_save).add_done_callback(
        lambda _: post_user_event(
            ReplaceByWidget(
                create_save_slot(slot, click_save_slot), from_button
            )
        )
    )


def menu_widget() -> PanelSpec:
    return PanelSpec(
        name="buttons",
        scroll_direction=ScrollDirection.HORIZONTAL,
        enter_animation=ENTER_ANIMATION,
        widgets=(
            ButtonSpec(
                text="save", on_click=create_save_panel(click_save_slot)
            ),
            ButtonSpec(text="title", on_click=title_scene),
        ),
    )


MENU_CONFIG = MenuConfig(menu_widget, WidgetLoader(TMX_DIR / "menu.tmx"))
