import sys
from pathlib import Path

sys.path.append(str((Path(__file__) / "../..").absolute()))

from interior_scene import interior_scene

from nextrpg import (
    Config,
    DebugConfig,
    Drawing,
    Game,
    Height,
    NineSlice,
    SayEventConfig,
    SayEventNineSliceBackgroundConfig,
    Size,
    Width,
)

drawing = Drawing("example/asset/bubble_background.png")
bubble = NineSlice(
    drawing, top=Height(14), left=Width(5), right=Width(5), bottom=Height(20)
)
tip = Drawing("example/asset/tip.png")
say_event = SayEventConfig(
    background=SayEventNineSliceBackgroundConfig(bubble, tip),
    padding=Size(25, 15),
)

Game(interior_scene, Config(say_event=say_event, debug=DebugConfig())).start()
