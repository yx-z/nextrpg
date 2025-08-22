from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from nextrpg.core.color import Color
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size
from nextrpg.draw.drawing import Drawing


@dataclass(frozen=True, kw_only=True)
class SpriteSheetSelection:
    row: int
    column: int


@dataclass(frozen=True, kw_only=True)
class SpriteSheet:
    resource: Drawing | str | Path
    num_row: int
    num_column: int
    color_key: Color | None = None

    @cached_property
    def grid(self) -> list[list[Drawing]]:
        return [
            [
                self.select(SpriteSheetSelection(row, column))
                for column in range(self.num_column)
            ]
            for row in range(self.num_row)
        ]

    def select(self, selection: SpriteSheetSelection) -> Drawing:
        width = self.drawing.width.value / self.num_column
        height = self.drawing.height.value / self.num_row
        top_left = Coordinate(width * selection.column, height * selection.row)
        size = Size(width, height)
        return self.drawing.crop(top_left, size)

    @cached_property
    def drawing(self) -> Drawing:
        return Drawing(self.resource, self.color_key)
