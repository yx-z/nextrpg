from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from nextrpg.core.coordinate import Coordinate
from nextrpg.draw.draw import Draw
from nextrpg.core.dimension import Size


@dataclass(frozen=True, kw_only=True)
class Selection:
    row: int
    column: int


@dataclass(frozen=True, kw_only=True)
class SpriteSheet:
    resource: Draw | str | Path
    num_row: int
    num_column: int

    def select(self, selection: Selection) -> Draw:
        width = self.draw.width / self.num_column
        height = self.draw.height / self.num_row
        top_left = Coordinate(width * selection.column, height * selection.row)
        size = Size(width, height)
        return self.draw.crop(top_left, size)

    @cached_property
    def draw(self) -> Draw:
        if isinstance(self.resource, Draw):
            return self.resource
        return Draw(self.resource)
