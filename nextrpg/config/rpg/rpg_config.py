from dataclasses import dataclass

from nextrpg.config.rpg.item_config import ItemConfig


@dataclass(frozen=True)
class RpgConfig:
    item: ItemConfig = ItemConfig()
