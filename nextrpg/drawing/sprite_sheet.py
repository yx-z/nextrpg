from dataclasses import dataclass
from functools import cached_property

from nextrpg.drawing.drawing import Drawing


@dataclass(frozen=True, kw_only=True)
class SpriteSheetSelection:
    row: int
    column: int


@dataclass(frozen=True, kw_only=True)
class SpriteSheet:
    drawing: Drawing
    num_rows: int
    num_columns: int

    @cached_property
    def grid(self) -> tuple[tuple[Drawing, ...], ...]:
        return tuple(
            tuple(
                self.select(SpriteSheetSelection(row=row, column=column))
                for column in range(self.num_columns)
            )
            for row in range(self.num_rows)
        )

    def __getitem__(self, item: tuple[int, int]) -> Drawing:
        row, col = item
        return self.select(SpriteSheetSelection(row=row, column=col))

    def select(self, selection: SpriteSheetSelection) -> Drawing:
        width = self.drawing.width / self.num_columns
        height = self.drawing.height / self.num_rows
        top_left = (
            (width * selection.column) * (height * selection.row)
        ).coordinate
        size = width * height
        area = top_left.as_top_left_of(size).rectangle_area_on_screen
        return self.drawing.crop(area)
