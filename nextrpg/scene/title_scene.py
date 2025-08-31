from dataclasses import dataclass
from typing import Self

from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing import Drawing
from nextrpg.geometry.coordinate import ORIGIN
from nextrpg.gui.button import Button
from nextrpg.scene.scene import Scene


@dataclass(frozen=True)
class TitleScene(Scene):
    background: Drawing
    new_game: Button
    load: Button
    quit: Button

    def tick(self, time_delta: Millisecond) -> Self:
        return self.background.drawing_on_screen(ORIGIN)
