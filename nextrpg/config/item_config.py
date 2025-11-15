from collections.abc import Callable
from dataclasses import dataclass
from enum import auto
from typing import TYPE_CHECKING

from frozendict import frozendict

from nextrpg.core.save import LoadFromSaveEnum

if TYPE_CHECKING:
    from nextrpg.drawing.drawing import Drawing


class ItemCategory(LoadFromSaveEnum):
    POTION = auto()
    WEAPON = auto()
    ARMOR = auto()
    ACCESSORY = auto()
    BOOK = auto()
    QUEST = auto()


@dataclass(frozen=True)
class ItemConfig:
    icons: frozendict[ItemCategory, Drawing | Callable[[], Drawing]] = (
        frozendict()
    )
