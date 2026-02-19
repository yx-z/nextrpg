from collections.abc import Callable
from dataclasses import dataclass, replace
from enum import auto
from functools import cached_property
from typing import TYPE_CHECKING, Self

from frozendict import frozendict

from nextrpg.core.save import LoadFromSaveEnum

if TYPE_CHECKING:
    from nextrpg.drawing.sprite import Sprite
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
    def __mul__(self, quantity: int) -> ItemKeyAndQuantity:
        return ItemKeyAndQuantity(self, quantity)

    def __rmul__(self, quantity: int) -> ItemKeyAndQuantity:
        return self * quantity

    def __neg__(self) -> ItemKeyAndQuantity:
        return self * -1

    def __pos__(self) -> ItemKeyAndQuantity:
        return self * 1


@dataclass(frozen=True)
class ItemKeyAndQuantity:
    key: BaseItemKey
    quantity: int

    @cached_property
    def tuple(self) -> tuple[BaseItemKey, int]:
        return self.key, self.quantity


@dataclass(frozen=True)
class ItemConfig:
    items: tuple[Item, ...] = ()
    icons: frozendict[ItemCategory, Sprite | Callable[[], Sprite]] = (
        frozendict()
    )

    def with_item(self, item: Item | tuple[Item, ...]) -> Self:
        from nextrpg.item.item import Item

        if isinstance(item, Item):
            items = self.items + (item,)
        else:
            items = self.items + item
        return replace(self, items=items)

    @cached_property
    def item_dict(self) -> dict[BaseItemKey, Item]:
        return {item.key: item for item in self.items}

    def get_icon(self, key: BaseItemKey) -> Sprite | None:
        return self.item_dict[key].icon
