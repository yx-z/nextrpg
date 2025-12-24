from collections.abc import Generator
from dataclasses import dataclass, replace
from functools import cached_property
from typing import TYPE_CHECKING, Any, Self, override

from nextrpg.config.rpg.item_config import BaseItemKey, ItemKeyAndQuantity
from nextrpg.core.save import LoadSavable
from nextrpg.event.event_as_attr import EventAsAttr
from nextrpg.event.event_transformer import register_rpg_event
from nextrpg.item.inventory import Inventory

if TYPE_CHECKING:
    from nextrpg.event.update_from_event import update_from_event


@dataclass(frozen=True)
class GameState(EventAsAttr, LoadSavable):
    inventory: Inventory = Inventory()

    @override
    @cached_property
    def save_data_this_class(self) -> dict[str, Any]:
        return {"inventory": self.inventory.save_data}

    @override
    @classmethod
    def load_this_class_from_save(cls, data: dict[str, Any]) -> Self:
        inventory = Inventory.load_from_save(data["inventory"])
        return cls(inventory)

    @register_rpg_event
    def update_event(
        self,
        *,
        inventory_update: (
            BaseItemKey
            | ItemKeyAndQuantity
            | tuple[BaseItemKey | ItemKeyAndQuantity, ...]
            | Inventory
            | None
        ) = None,
    ) -> Generator[None, None, None]:
        from nextrpg.event.update_from_event import update_from_event

        updated = self.update(inventory_update=inventory_update)
        yield update_from_event(updated)

    def update(
        self,
        *,
        inventory_update: (
            BaseItemKey
            | ItemKeyAndQuantity
            | tuple[BaseItemKey | ItemKeyAndQuantity, ...]
            | Inventory
            | None
        ) = None,
    ) -> Self:
        updated = self
        if inventory_update:
            updated = updated._update_inventory(inventory_update)
        return updated

    def _update_inventory(
        self,
        arg: (
            BaseItemKey
            | ItemKeyAndQuantity
            | tuple[BaseItemKey | ItemKeyAndQuantity, ...]
            | Inventory
        ),
    ) -> Self:
        if isinstance(arg, Inventory):
            inventory = arg
        else:
            inventory = self.inventory + arg
        return replace(self, inventory=inventory)
