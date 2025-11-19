from functools import cache

from example.component.component_common import TMX_DIR
from example.component.save_slot import (
    ENTER_ANIMATION,
    create_save_panel,
    create_save_slot,
)
from example.component.title import title
from example.scene.character import create_player_placeholder
from nextrpg import (
    Button,
    ButtonOnScreen,
    GameSave,
    GameState,
    MapScene,
    MenuScene,
    PanelOnScreen,
    SaveIo,
    ScrollDirection,
    TmxLoader,
    TransitionScene,
    WidgetGroup,
    WidgetOnScreen,
    last_scene,
)


@cache
def tmx() -> TmxLoader:
    tmx_path = TMX_DIR / "menu.tmx"
    return TmxLoader(tmx_path)


def title_scene(button: ButtonOnScreen, state: GameState) -> TransitionScene:
    assert isinstance(
        menu_scene := last_scene(), MenuScene
    ), f"Expect button called on a MenuScene. Got {menu_scene}"
    menu_scene.parent.stop_sound()
    return TransitionScene(title)


def menu_widget() -> WidgetGroup:
    save_panel = create_save_panel(click_save)
    save_button = Button(name="save", on_click=save_panel)

    title_button = Button(name="title", on_click=title_scene)
    widgets = (save_button, title_button)
    return WidgetGroup(
        children=widgets,
        scroll_direction=ScrollDirection.HORIZONTAL,
        enter_animation=ENTER_ANIMATION,
    )


def click_save(
    slot: int, from_button: ButtonOnScreen, state: GameState
) -> WidgetOnScreen:
    assert isinstance(map_scene := from_button.root, MapScene)
    game_save = GameSave(create_player_placeholder, state, map_scene)
    save_io = SaveIo(str(slot))
    save_io.save(game_save).result()

    assert isinstance(panel := from_button.parent, PanelOnScreen)
    button = create_save_slot(slot, click_save)(panel)
    assert panel.parent, f"Panel should have parent. Got {panel}"
    button_on_screen = button.with_parent(panel.parent)
    return panel.replace(from_button, button_on_screen)
