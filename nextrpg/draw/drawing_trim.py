from __future__ import annotations

from dataclasses import dataclass

from nextrpg.geometry.dimension import Pixel


@dataclass(frozen=True, kw_only=True)
class DrawingTrim:
    top: Pixel = 0
    left: Pixel = 0
    bottom: Pixel = 0
    right: Pixel = 0
