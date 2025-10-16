from enum import Enum, auto
from functools import cached_property


class Anchor(Enum):
    TOP_LEFT = auto()
    TOP_CENTER = auto()
    TOP_RIGHT = auto()
    CENTER_LEFT = auto()
    CENTER = auto()
    CENTER_RIGHT = auto()
    BOTTOM_LEFT = auto()
    BOTTOM_CENTER = auto()
    BOTTOM_RIGHT = auto()

    @cached_property
    def __neg__(self) -> Anchor:
        return _OPPOSITE_ANCHOR[self]


_OPPOSITE_ANCHOR = {
    Anchor.TOP_LEFT: Anchor.BOTTOM_RIGHT,
    Anchor.TOP_CENTER: Anchor.BOTTOM_CENTER,
    Anchor.TOP_RIGHT: Anchor.BOTTOM_LEFT,
    Anchor.CENTER_LEFT: Anchor.CENTER_RIGHT,
    Anchor.CENTER: Anchor.CENTER,
    Anchor.CENTER_RIGHT: Anchor.CENTER_LEFT,
    Anchor.BOTTOM_LEFT: Anchor.TOP_RIGHT,
    Anchor.BOTTOM_CENTER: Anchor.TOP_CENTER,
    Anchor.BOTTOM_RIGHT: Anchor.TOP_LEFT,
}
