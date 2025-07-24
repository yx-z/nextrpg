from dataclasses import dataclass
from typing import NamedTuple

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size
from nextrpg.draw.draw_on_screen import DrawOnScreen
from nextrpg.draw.drawing import Drawing


class DrawingRelativeTo(NamedTuple):
    drawing: Drawing | DrawingGroup
    relative_to: Size


@dataclass(frozen=True)
class DrawingGroup:
    leader: Drawing
    followers: tuple[DrawingRelativeTo, ...]

    def draw_on_screens(
        self, leader_coordinate: Coordinate
    ) -> tuple[DrawOnScreen, ...]:
        res = [DrawOnScreen(leader_coordinate, self.leader)]
        for drawing, relative_to in self.followers:
            coord = leader_coordinate + relative_to
            if isinstance(drawing, Drawing):
                res.append(DrawOnScreen(coord, drawing))
            else:
                res += drawing.draw_on_screens(coord)
        return tuple(res)
