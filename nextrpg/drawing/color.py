from dataclasses import dataclass
from functools import cached_property
from typing import Self, override

from nextrpg.core.save import LoadFromSave
from nextrpg.core.time import Percentage

type Alpha = int


@dataclass(frozen=True)
class Color(LoadFromSave):
    red: int
    green: int
    blue: int
    alpha: Alpha = 255

    def with_alpha(self, alpha: Alpha) -> Color:
        return Color(self.red, self.green, self.blue, alpha)

    def with_percentage_alpha(self, percentage: Percentage) -> Color:
        alpha = alpha_from_percentage(percentage)
        return self.with_alpha(alpha)

    @cached_property
    def pygame(self) -> tuple[int, ...]:
        return self.red, self.green, self.blue, self.alpha

    @override
    @cached_property
    def save_data_this_class(self) -> tuple[int, ...]:
        return self.pygame

    @override
    @classmethod
    def load_this_class_from_save(cls, data: list[int]) -> Self:
        assert (
            len(data) == 4
        ), f"Color only takes [red, green, blue, alpha]. Got {data}."
        return cls(*data)


RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
BLACK = Color(0, 0, 0)
WHITE = Color(255, 255, 255)
TRANSPARENT = Color(0, 0, 0, 0)


def alpha_from_percentage(percentage: Percentage) -> Alpha:
    clamped = max(0.0, min(1.0, percentage))
    return int(255 * clamped)
