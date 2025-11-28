from example.component.component_common import TMX_DIR
from example.component.save_slot import create_save_panel
from example.scene.character import create_player
from example.scene.exterior_scene import exterior_scene
from nextrpg import (
    Button,
    ButtonOnScreen,
    GameSave,
    GameSaveMeta,
    GameState,
    MapScene,
    Panel,
    PanelOnScreen,
    SaveIo,
    Scene,
    ScrollDirection,
    TmxWidgetLoader,
    TransitionScene,
    quit,
)


def click_start(start: ButtonOnScreen, state: GameState) -> TransitionScene:
    def new_game(st: GameState) -> MapScene:
        player = create_player()
        return exterior_scene(player, st)

    return TransitionScene(new_game)


def title(state: GameState) -> PanelOnScreen:
    start = Button(text="start", on_click=click_start)

    load_panel = create_save_panel(click_load)
    load = Button(text="load", on_click=load_panel)

    # TODO: Implement on_click.
    options = Button(text="options", on_click=lambda _, __: print("Options..."))
    exit_button = Button(text="exit", on_click=quit)

    children = (start, load, options, exit_button)
    panel = Panel(
        name="buttons",
        children=children,
        scroll_direction=ScrollDirection.HORIZONTAL,
    )

    tmx_widget_loader = TmxWidgetLoader(TMX_DIR / "title.tmx")
    background = tmx_widget_loader.background("background")
    name_to_on_screens = tmx_widget_loader.name_to_on_screens
    return PanelOnScreen(
        widget=panel,
        background=background,
        name_to_on_screens=name_to_on_screens,
        is_selected=True,
    )


def click_load(
    button: ButtonOnScreen, state: GameState, slot: int
) -> TransitionScene | None:
    save_io = SaveIo(str(slot))

    def load_game(st: GameState) -> tuple[Scene, GameState]:
        game = save_io.load(GameSave)
        return game.scene, game.state

    if save_io.load(GameSaveMeta):
        return TransitionScene(load_game)
    return None
