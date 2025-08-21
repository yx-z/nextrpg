from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

from nextrpg.core.dimension import Size
from nextrpg.draw.drawing import Drawing

if TYPE_CHECKING:
    from nextrpg.draw.drawing_group import DrawingGroup


class RelativeDrawing(NamedTuple):
    drawing: Drawing | DrawingGroup
    shift: Size
