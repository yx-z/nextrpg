from enum import auto

from nextrpg import BaseItemKey, Drawing, Item, ItemConfig


class ItemKey(BaseItemKey):
    FRUIT = auto()


ITEMS = (Item(ItemKey.FRUIT, "fruit", icon_input=Drawing("icon/fruit.png")),)
ITEM_CONFIG = ItemConfig(items=ITEMS)
