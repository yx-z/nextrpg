from dataclasses import dataclass

from nextrpg.geometry.size import Height, Width


@dataclass(frozen=True)
class TextGroupConfig:
    line_spacing: Height = Height(8)
    margin: Width = Width(2)
