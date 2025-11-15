from dataclasses import dataclass, field, replace
from typing import Self

from frozendict import frozendict

from nextrpg.config.config import config
from nextrpg.config.item_config import BaseItemKey, ItemCategory, ItemConfig


@dataclass(frozen=True)
class Inventory:
    items: frozendict[BaseItemKey, int] = frozendict()
    config: ItemConfig = field(default_factory=lambda: config().item)

    def __contains__(self, item: BaseItemKey) -> bool:
        return item in self.items

    def __sub__(self, item: BaseItemKey) -> Self | None:
        if item not in self:
            return None
        res = self.items | {item: self.items[item] - 1}
        return replace(self, items=frozendict(res))

    def __add__(self, item: BaseItemKey) -> Self:
        res = self.items | {item: self.items.get(item, 0) + 1}
        return replace(self, items=frozendict(res))

    def get_category(
        self, category: ItemCategory
    ) -> frozendict[BaseItemKey, int]:
        res = {
            item: quantity
            for item, quantity in self.items.items()
            if (it := self.config.get_item(item)) and it.category is category
        }
        return frozendict(res)
