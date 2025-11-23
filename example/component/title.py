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
    SaveIo,
    Scene,
    ScrollDirection,
    TmxLoader,
    TmxWidgetGroupOnScreen,
    TransitionScene,
    WidgetGroup,
    quit,
)


def click_start(start: ButtonOnScreen, state: GameState) -> TransitionScene:
    def new_game(st: GameState) -> MapScene:
        player = create_player()
        return exterior_scene(player, st)

    return TransitionScene(new_game)


def title(state: GameState) -> TmxWidgetGroupOnScreen:
    start = Button(name="start", on_click=click_start)

    load_panel = create_save_panel(click_load)
    load = Button(name="load", on_click=load_panel)

    # TODO: Implement.
    options = Button(name="options", on_click=lambda _, __: print("Options..."))
    exit_button = Button(name="exit", on_click=quit)

    children = (start, load, options, exit_button)
    group = WidgetGroup(
        children=children, scroll_direction=ScrollDirection.HORIZONTAL
    )
    tmx_path = TMX_DIR / "title.tmx"
    tmx_loader = TmxLoader(tmx_path)
    return TmxWidgetGroupOnScreen(
        tmx=tmx_loader, background_layer="background", widget=group
    )


def click_load(
    button: ButtonOnScreen, state: GameState, slot: int
) -> TransitionScene | None:
    save_io = SaveIo(str(slot))

    def load_game(st: GameState) -> tuple[Scene, GameState]:
        game = save_io.load(GameSave)
        assert game, f"Expect GameSave at save slot {slot}"
        return game.scene, game.state

    if save_io.load(GameSaveMeta):
        return TransitionScene(load_game)
    return None
