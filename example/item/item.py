from enum import auto

from nextrpg import BaseItemKey, Item, ItemConfig


class ItemKey(BaseItemKey):
    FRUIT = auto()


ITEMS = (Item(ItemKey.FRUIT, "fruit"),)
ITEM_CONFIG = ItemConfig(items=ITEMS)
