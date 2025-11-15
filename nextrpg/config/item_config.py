from collections.abc import Callable
from dataclasses import dataclass, replace
from enum import auto
from typing import TYPE_CHECKING, Self

from frozendict import frozendict

from nextrpg.core.save import LoadFromSaveEnum

if TYPE_CHECKING:
    from nextrpg.drawing.drawing import Drawing
    from nextrpg.item.item import Item


class ItemCategory(LoadFromSaveEnum):
    POTION = auto()
    WEAPON = auto()
    ARMOR = auto()
    ACCESSORY = auto()
    BOOK = auto()
    QUEST = auto()
    GENERIC = auto()


class BaseItemKey(LoadFromSaveEnum):
    pass


@dataclass(frozen=True)
class ItemConfig:
    items: frozendict[BaseItemKey, Item] = frozendict()
    icons: frozendict[ItemCategory, Drawing | Callable[[], Drawing]] = (
        frozendict()
    )

    def with_item(self, key: BaseItemKey, item: Item) -> Self:
        items = self.items | {key: item}
        return replace(self, items=items)

    def get_item(self, item: BaseItemKey) -> Item | None:
        return self.items.get(item)
