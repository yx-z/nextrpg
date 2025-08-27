from __future__ import annotations

from dataclasses import dataclass

from nextrpg.geometry.dimension import Height, Width


@dataclass(frozen=True)
class DrawingTrim:
    top: Height = Height(0)
    left: Width = Width(0)
    bottom: Height = Height(0)
    right: Width = Width(0)
