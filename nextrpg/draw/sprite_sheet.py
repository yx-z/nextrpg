from dataclasses import dataclass
from functools import cached_property

from nextrpg.draw.color import Color
from nextrpg.draw.drawing import Drawing


@dataclass(frozen=True, kw_only=True)
class SpriteSheetSelection:
    row: int
    column: int


@dataclass(frozen=True, kw_only=True)
class SpriteSheet:
    drawing: Drawing
    num_row: int
    num_column: int
    color_key: Color | None = None

    @cached_property
    def grid(self) -> tuple[tuple[Drawing, ...], ...]:
        return tuple(
            tuple(
                self.select(SpriteSheetSelection(row=row, column=column))
                for column in range(self.num_column)
            )
            for row in range(self.num_row)
        )

    def select(self, selection: SpriteSheetSelection) -> Drawing:
        width = self.drawing.width / self.num_column
        height = self.drawing.height / self.num_row
        top_left = (
            (width * selection.column) * (height * selection.row)
        ).coordinate
        size = width * height
        area = top_left.anchor(size).rectangle_area_on_screen
        return self.drawing.crop(area)
