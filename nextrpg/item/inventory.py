from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import Self, override

from frozendict import frozendict

from nextrpg.config.config import config
from nextrpg.config.rpg.item_config import (
    BaseItemKey,
    ItemCategory,
    ItemConfig,
    ItemKeyAndQuantity,
)
from nextrpg.core.save import LoadFromSave


@dataclass(frozen=True)
class Inventory(LoadFromSave):
    items: frozendict[BaseItemKey, int] = frozendict()
    config: ItemConfig = field(default_factory=lambda: config().rpg.item)

    @override
    @cached_property
    def save_data_this_class(
        self,
    ) -> list[tuple[dict[str, str | tuple[str, ...]], int]]:
        return [
            (key.save_data, quantity) for key, quantity in self.items.items()
        ]

    @override
    @classmethod
    def load_this_class_from_save(
        cls, data: list[tuple[dict[str, str | tuple[str, ...]], int]]
    ) -> Self:
        res = {BaseItemKey.load_from_save(key): qty for key, qty in data}
        return cls(frozendict(res))

    def __contains__(
        self,
        item: (
            BaseItemKey
            | ItemKeyAndQuantity
            | tuple[BaseItemKey | ItemKeyAndQuantity, ...]
        ),
    ) -> bool:
        return all(
            self.count(it) >= qty for it, qty in _item_and_quantities(item)
        )

    def __add__(
        self,
        item: (
            BaseItemKey
            | ItemKeyAndQuantity
            | tuple[BaseItemKey | ItemKeyAndQuantity, ...]
        ),
    ) -> Self:
        updates = {
            it: self.count(it) + qty for it, qty in _item_and_quantities(item)
        }
        res = self.items | updates
        return replace(self, items=frozendict(res))

    def count(self, item: BaseItemKey) -> int:
        return self.items.get(item, 0)

    def get_category(self, category: ItemCategory) -> dict[BaseItemKey, int]:
        return {
            key: quantity
            for key, quantity in self.items.items()
            if (it := self.config.item_dict[key]) and it.category is category
        }


def _item_and_quantities(
    item: (
        BaseItemKey
        | ItemKeyAndQuantity
        | tuple[BaseItemKey | ItemKeyAndQuantity, ...]
    ),
) -> list[tuple[BaseItemKey, int]]:
    if isinstance(item, BaseItemKey | ItemKeyAndQuantity):
        args = (item,)
    else:
        args = item
    return [
        arg.tuple if isinstance(arg, ItemKeyAndQuantity) else (arg, 1)
        for arg in args
    ]
