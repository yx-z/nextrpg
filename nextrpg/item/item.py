from dataclasses import dataclass, replace
from enum import auto
from functools import cached_property
from typing import Self

from nextrpg.core.dataclass_with_default import dataclass_with_default
from nextrpg.core.save import LoadFromSaveEnum
from nextrpg.drawing.animation_like import AnimationLike


class ItemKey(LoadFromSaveEnum):
    pass


class ItemCategory(LoadFromSaveEnum):
    CONSUMABLE = auto()
    EQUIPMENT = auto()
    UNIQUE = auto()


@dataclass_with_default(frozen=True)
class Item:
    key: ItemKey
    name: str
    description: str
    category: ItemCategory
    icon: AnimationLike | None = None

    @cached_property
    def singleton(self) -> ItemAndQuantity:
        return self.with_quantity(1)

    def with_quantity(self, quantity: int) -> ItemAndQuantity:
        return ItemAndQuantity(self, quantity)


@dataclass(frozen=True)
class ItemAndQuantity:
    item: Item
    quantity: int

    @cached_property
    def increment(self) -> Self:
        return self + 1

    @cached_property
    def decrement(self) -> Self:
        return self - 1

    def __add__(self, quantity: int) -> Self:
        return replace(self, quantity=self.quantity + quantity)

    def __sub__(self, quantity: int) -> Self:
        return self + -quantity
