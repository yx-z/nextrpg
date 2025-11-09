from collections.abc import Callable

from example.component.component_common import TMX_DIR
from example.component.save_slot import create_save_panel
from example.scene.character import create_player
from example.scene.interior_scene import interior_scene
from nextrpg import (
    ButtonOnScreen,
    DefaultButton,
    GameSave,
    MapScene,
    SaveIo,
    Scene,
    ScrollDirection,
    TmxLoader,
    TmxWidgetGroupOnScreen,
    TransitionScene,
    WidgetGroup,
    WidgetOnScreen,
    load_save_meta,
    quit,
)


def new_game() -> MapScene:
    player = create_player()
    return interior_scene(player)


def click_start(start: ButtonOnScreen) -> TransitionScene:
    return TransitionScene(new_game)


def title() -> TmxWidgetGroupOnScreen:
    start = DefaultButton(name="start", on_click=click_start)

    load_panel = create_save_panel("load_panel", click_load)
    load = DefaultButton(name="load", on_click=load_panel)

    # TODO: Implement.
    options = DefaultButton(
        name="options", on_click=lambda _: print("Options...")
    )

    exit_button = DefaultButton(name="exit", on_click=quit)

    children = (start, load, options, exit_button)
    group = WidgetGroup(
        children=children, scroll_direction=ScrollDirection.HORIZONTAL
    )
    tmx_path = TMX_DIR / "title.tmx"
    tmx_loader = TmxLoader(tmx_path)
    return TmxWidgetGroupOnScreen(
        tmx=tmx_loader, background_resource="background", widget=group
    )


def click_load(
    i: int,
) -> Callable[[ButtonOnScreen], WidgetOnScreen | Scene | None]:
    def load_game() -> Scene:
        save_io = SaveIo(str(i))
        assert (
            game := save_io.load(GameSave)
        ), f"Expect GameSave at save slot {i}"
        return game.scene

    def load_save_slot(_: ButtonOnScreen) -> TransitionScene | None:
        if load_save_meta(str(i)):
            return TransitionScene(load_game)
        return None

    return load_save_slot
