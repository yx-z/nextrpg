from collections.abc import Callable
from dataclasses import dataclass

from nextrpg.config.config import config
from nextrpg.config.rpg.item_config import BaseItemKey, ItemCategory
from nextrpg.drawing.sprite import Sprite


@dataclass(frozen=True)
class Item:
    key: BaseItemKey
    name: str
    description: str = ""
    icon_input: Sprite | Callable[[], Sprite] | None = None
    category: ItemCategory = ItemCategory.GENERIC

    @property
    def icon(self) -> Sprite | None:
        if (source := self.icon_input) is None:
            source = config().rpg.item.icons.get(self.category)
        if callable(source):
            return source()
        return source

    def __eq__(self, other: Item) -> bool:
        return self.key is other.key
