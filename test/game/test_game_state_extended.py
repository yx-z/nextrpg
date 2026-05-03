"""Extended tests for nextrpg.game.game_state module."""
import pytest
from enum import auto
from frozendict import frozendict
from nextrpg.game.game_state import GameState
from nextrpg.item.inventory import Inventory
from nextrpg.config.rpg.item_config import BaseItemKey, ItemKeyAndQuantity


class MockItemKey(BaseItemKey):
    SWORD = auto()
    POTION = auto()


class TestGameStateUpdate:
    """Tests for GameState.update method."""

    def test_update_with_none_returns_same(self):
        """Test update with None inventory_update returns same state."""
        state = GameState()
        updated = state.update(inventory_update=None)
        assert updated == state

    def test_update_with_item_key(self):
        """Test update with a single item key adds one item."""
        state = GameState()
        updated = state.update(inventory_update=MockItemKey.SWORD)
        assert updated.inventory.count(MockItemKey.SWORD) == 1

    def test_update_with_item_key_and_quantity(self):
        """Test update with ItemKeyAndQuantity adds the correct amount."""
        state = GameState()
        updated = state.update(inventory_update=MockItemKey.POTION * 5)
        assert updated.inventory.count(MockItemKey.POTION) == 5

    def test_update_with_inventory_replaces_inventory(self):
        """Test update with an Inventory object replaces the inventory."""
        state = GameState()
        new_inv = Inventory(items=frozendict({MockItemKey.SWORD: 10}))
        updated = state.update(inventory_update=new_inv)
        assert updated.inventory is new_inv
        assert updated.inventory.count(MockItemKey.SWORD) == 10

    def test_update_with_tuple_of_items(self):
        """Test update with a tuple of items adds all of them."""
        state = GameState()
        updated = state.update(
            inventory_update=(MockItemKey.SWORD, MockItemKey.POTION * 3)
        )
        assert updated.inventory.count(MockItemKey.SWORD) == 1
        assert updated.inventory.count(MockItemKey.POTION) == 3

    def test_update_does_not_mutate_original(self):
        """Test update returns a new state without mutating the original."""
        state = GameState()
        _ = state.update(inventory_update=MockItemKey.SWORD)
        assert state.inventory.count(MockItemKey.SWORD) == 0

    def test_chained_updates(self):
        """Test multiple chained updates accumulate items."""
        state = GameState()
        state = state.update(inventory_update=MockItemKey.SWORD)
        state = state.update(inventory_update=MockItemKey.SWORD)
        state = state.update(inventory_update=MockItemKey.POTION * 2)
        assert state.inventory.count(MockItemKey.SWORD) == 2
        assert state.inventory.count(MockItemKey.POTION) == 2


class TestGameStateSaveLoadExtended:
    """Extended tests for GameState save/load."""

    def test_save_load_with_items(self):
        """Test save/load round-trip preserves inventory items."""
        state = GameState()
        state = state.update(inventory_update=MockItemKey.SWORD * 3)
        
        save_data = state.save_data_this_class
        loaded = GameState.load_this_class_from_save(save_data)
        
        assert loaded.inventory.count(MockItemKey.SWORD) == 3

    def test_save_data_structure(self):
        """Test save data has expected structure."""
        state = GameState()
        save_data = state.save_data_this_class
        
        assert isinstance(save_data, dict)
        assert "inventory" in save_data
