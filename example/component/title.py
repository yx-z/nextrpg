from functools import cache
from pathlib import Path

from example.scene.interior_scene import interior_scene
from nextrpg import (
    DefaultButton,
    ScrollDirection,
    TmxLoader,
    TmxWidgetGroupOnScreen,
    TransitionScene,
    WidgetGroup,
    quit,
)


@cache
def title() -> TmxWidgetGroupOnScreen:
    scene = TransitionScene(interior_scene)
    start = DefaultButton(name="start", on_click=scene)
    load = DefaultButton(name="load", on_click=quit)
    options = DefaultButton(name="options", on_click=quit)
    exit_button = DefaultButton(name="exit", on_click=quit)

    group = WidgetGroup(
        children=(start, load, options, exit_button),
        scroll_direction=ScrollDirection.HORIZONTAL,
    )

    tmx_path = Path("example/component/title.tmx")
    tmx_loader = TmxLoader(tmx_path)
    return TmxWidgetGroupOnScreen(
        tmx=tmx_loader, background="background", widget=group
    )
