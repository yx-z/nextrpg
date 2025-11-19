from collections.abc import Callable
from dataclasses import dataclass
from functools import cached_property

from nextrpg.config.config import config
from nextrpg.config.item_config import BaseItemKey, ItemCategory
from nextrpg.drawing.drawing import Drawing


@dataclass(frozen=True)
class Item:
    key: BaseItemKey
    name: str
    description: str = ""
    icon_input: Drawing | Callable[[], Drawing] | None = None
    category: ItemCategory = ItemCategory.GENERIC

    @cached_property
    def icon(self) -> Drawing | None:
        if (source := self.icon_input) is None:
            source = config().item.icons.get(self.category)
        if callable(source):
            return source()
        return source

    def __eq__(self, other: Item) -> bool:
        return self.key is other.key
