from dataclasses import dataclass

from nextrpg.geometry.dimension import Height, Width
from nextrpg.geometry.padding import Padding, padding_for_both_sides


@dataclass(frozen=True)
class PanelConfig:
    children_padding: Padding = padding_for_both_sides(Width(10), Height(10))
