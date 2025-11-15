from dataclasses import dataclass, replace
from typing import Self

from frozendict import frozendict

from nextrpg.item.item import Item, ItemCategory


@dataclass(frozen=True)
class Inventory:
    items: frozendict[Item, int] = frozendict()

    def __contains__(self, item: Item) -> bool:
        return item in self.items

    def __sub__(self, item: Item) -> Self | None:
        if item not in self:
            return None
        res = self.items | {item: self.items[item] - 1}
        return replace(self, items=frozendict(res))

    def __add__(self, item: Item) -> Self:
        res = self.items | {item: self.items.get(item, 0) + 1}
        return replace(self, items=frozendict(res))

    def get_category(self, category: ItemCategory) -> frozendict[Item, int]:
        res = {
            item: quantity
            for item, quantity in self.items.items()
            if item.category is category
        }
        return frozendict(res)
