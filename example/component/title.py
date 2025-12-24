from typing import Any

from example.component.save_slot import TMX_DIR, create_save_panel
from example.scene.character import create_player
from example.scene.exterior_scene import exterior_scene
from nextrpg import (
    Button,
    ButtonSpec,
    GameSave,
    GameSaveMeta,
    GameState,
    MapScene,
    Panel,
    PanelSpec,
    SaveIo,
    Scene,
    ScrollDirection,
    TransitionScene,
    WidgetLoader,
    post_quit_event,
)


def click_start(start: Button, state: GameState) -> TransitionScene:
    def new_game(st: GameState) -> MapScene:
        player = create_player()
        map_spec = exterior_scene(player, st)
        return map_spec()

    return TransitionScene(new_game)


def click_load(
    button: Button, state: GameState, slot: str
) -> TransitionScene | None:
    save_io = SaveIo(slot)

    def load_game(st: GameState) -> tuple[Scene, GameState]:
        game = save_io.load(GameSave)
        assert game, f"Save slot #{slot} is empty."
        return game.scene, game.state

    if save_io.load(GameSaveMeta):
        return TransitionScene(load_game)
    return None


def title(*_: Any) -> Panel:
    tmx = WidgetLoader(TMX_DIR / "title.tmx")
    return Panel(
        background=tmx.image_layer("background"),
        name_to_on_screens=tmx.name_to_on_screens,
        is_selected=True,
        spec=PanelSpec(
            name="buttons",
            scroll_direction=ScrollDirection.HORIZONTAL,
            widgets=(
                ButtonSpec(text="start", on_click=click_start),
                ButtonSpec(text="load", on_click=create_save_panel(click_load)),
                ButtonSpec(text="options", on_click=print),  # TODO: Implement.
                ButtonSpec(text="exit", on_click=post_quit_event),
            ),
        ),
    )
