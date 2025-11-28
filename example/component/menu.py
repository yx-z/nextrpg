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
    Panel,
    PanelOnScreen,
    SaveIo,
    ScrollDirection,
    TmxWidgetLoader,
    TransitionScene,
    last_scene,
)


def tmx() -> TmxWidgetLoader:
    return TmxWidgetLoader(TMX_DIR / "menu.tmx")


def title_scene(button: ButtonOnScreen, state: GameState) -> TransitionScene:
    menu_scene = last_scene()
    assert isinstance(
        menu_scene, MenuScene
    ), f"Expect button called on a MenuScene. Got {menu_scene}"
    menu_scene.parent.stop_sound()
    return TransitionScene(title)


def menu_widget() -> Panel:
    save_panel = create_save_panel(click_save_slot)
    save_button = Button(text="save", on_click=save_panel)

    title_button = Button(text="title", on_click=title_scene)
    buttons = (save_button, title_button)
    return Panel(
        name="buttons",
        children=buttons,
        scroll_direction=ScrollDirection.HORIZONTAL,
        enter_animation=ENTER_ANIMATION,
    )


def click_save_slot(
    from_button: ButtonOnScreen, state: GameState, slot: int
) -> PanelOnScreen:
    map_scene = from_button.root
    assert isinstance(map_scene, MapScene)
    game_save = GameSave(create_player_placeholder, state, map_scene)
    save_io = SaveIo(str(slot))
    save_io.save(game_save).result()

    panel = from_button.parent
    assert isinstance(panel, PanelOnScreen)
    button = create_save_slot(slot, click_save_slot)
    child = button.with_parent(panel).select
    return panel.replace(child)
