import sys
from pathlib import Path

sys.path.append(str((Path(__file__) / "../..").absolute()))

from interior_scene import interior_scene

from nextrpg import (
    Config,
    DebugConfig,
    Drawing,
    Game,
    NineSlice,
    SayEventConfig,
    SayEventNineSliceBackgroundConfig,
)


def bubble() -> NineSlice:
    drawing = Drawing("example/asset/bubble_background.png")
    return NineSlice(drawing, top=10, left=5, right=5, bottom=20)


def tip() -> Drawing:
    return Drawing("example/asset/tip.png")


say_event = SayEventConfig(
    background=SayEventNineSliceBackgroundConfig(bubble, tip),
)
Game(interior_scene, Config(debug=DebugConfig(), say_event=say_event)).start()
