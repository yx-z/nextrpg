from collections.abc import Callable
from dataclasses import field
from functools import cached_property

from nextrpg.config.config import config
from nextrpg.config.item_config import ItemCategory, ItemConfig
from nextrpg.core.dataclass_with_default import dataclass_with_default, default
from nextrpg.core.save import LoadFromSaveEnum
from nextrpg.drawing.drawing import Drawing


class ItemKey(LoadFromSaveEnum):
    pass


@dataclass_with_default(frozen=True)
class Item:
    key: ItemKey
    name: str
    description: str
    category: ItemCategory
    config: ItemConfig = field(default_factory=lambda: config().item)
    icon_input: Drawing | Callable[[], Drawing] | None = default(
        lambda self: self.config.icons.get(self.category)
    )

    @cached_property
    def icon(self) -> Drawing:
        if isinstance(self.icon_input, Drawing):
            return self.icon_input
        return self.icon_input()

    def __eq__(self, other: Item) -> bool:
        return self.key is other.key
