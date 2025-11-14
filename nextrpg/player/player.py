from dataclasses import dataclass

from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.item.inventory import Inventory


@dataclass(frozen=True)
class Player:
    on_screen: PlayerOnScreen
    inventory: Inventory
