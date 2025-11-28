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
    Panel,
    PanelOnScreen,
    SaveIo,
    ScrollDirection,
    TmxWidgetLoader,
    TransitionScene,
    WidgetGroup,
    WidgetOnScreen,
    last_scene,
)


def tmx() -> TmxWidgetLoader:
    return TmxWidgetLoader(TMX_DIR / "menu.tmx")


def title_scene(button: ButtonOnScreen, state: GameState) -> TransitionScene:
    map_scene: WidgetOnScreen = last_scene()
    assert isinstance(
        map_scene, WidgetOnScreen
    ), f"Expect WidgetOnScreen. Got {map_scene}."
    root: MapScene = map_scene.root
    assert isinstance(root, MapScene), f"Expect MapScene. Got {root}."
    root.stop_sound()
    return TransitionScene(title)


def menu_widget() -> WidgetGroup:
    save_panel = create_save_panel(click_save_slot)
    save_button = Button(text="save", on_click=save_panel)

    title_button = Button(text="title", on_click=title_scene)
    buttons = (save_button, title_button)
    panel = Panel(
        name="buttons",
        children=buttons,
        scroll_direction=ScrollDirection.HORIZONTAL,
    )
    return WidgetGroup(
        children=(panel,),
        enter_animation=ENTER_ANIMATION,
    )


def click_save_slot(
    from_button: ButtonOnScreen, state: GameState, slot: int
) -> PanelOnScreen:
    game_save = GameSave(create_player_placeholder, state, from_button.root)
    save_io = SaveIo(str(slot))
    save_io.save(game_save).result()

    panel: PanelOnScreen = from_button.parent
    assert isinstance(
        panel, PanelOnScreen
    ), f"Expect PanelOnScreen. Got {panel}."
    button = create_save_slot(slot, click_save_slot)
    child = button.with_parent(panel).select
    return panel.replace(child)
