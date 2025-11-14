from dataclasses import dataclass

from nextrpg.item.item import ItemAndQuantity


@dataclass(frozen=True)
class Inventory:
    items: tuple[ItemAndQuantity]
