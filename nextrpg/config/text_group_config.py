from dataclasses import dataclass

from nextrpg.geometry.dimension import Height, Width


@dataclass(frozen=True, slots=True)
class TextGroupConfig:
    line_spacing: Height = Height(8)
    margin: Width = Width(2)
