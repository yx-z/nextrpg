from dataclasses import dataclass, field
from functools import cached_property

from nextrpg.config import config
from nextrpg.coordinate import Coordinate
from nextrpg.core import Rgba
from nextrpg.draw_on_screen import DrawOnScreen, Rectangle
from nextrpg.gui import gui_size
from nextrpg.scene.scene import Scene


@dataclass
class ColorScene(Scene):
    color: Rgba = field(default_factory=lambda: config().gui.background_color)

    @cached_property
    def _draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        return (Rectangle(Coordinate(0, 0), gui_size()).fill(self.color),)
