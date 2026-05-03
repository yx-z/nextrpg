"""Tests for nextrpg.item.inventory module."""
import pytest
from enum import auto
from frozendict import frozendict
from nextrpg.item.inventory import Inventory
from nextrpg.config.rpg.item_config import BaseItemKey, ItemKeyAndQuantity


class MockItemKey(BaseItemKey):
    SWORD = auto()
    POTION = auto()
    SHIELD = auto()


class TestInventoryCreation:
    """Tests for Inventory creation."""

    def test_empty_inventory(self):
        """Test creating an empty inventory."""
        inv = Inventory()
        assert len(inv.items) == 0

    def test_inventory_with_items(self):
        """Test creating an inventory with initial items."""
        items = frozendict({MockItemKey.SWORD: 3, MockItemKey.POTION: 5})
        inv = Inventory(items=items)
        assert inv.count(MockItemKey.SWORD) == 3
        assert inv.count(MockItemKey.POTION) == 5

    def test_inventory_is_frozen(self):
        """Test that Inventory is immutable."""
        inv = Inventory()
        with pytest.raises(Exception):
            inv.items = frozendict()


class TestInventoryCount:
    """Tests for Inventory.count method."""

    def test_count_existing_item(self):
        """Test counting an item that exists in inventory."""
        items = frozendict({MockItemKey.SWORD: 5})
        inv = Inventory(items=items)
        assert inv.count(MockItemKey.SWORD) == 5

    def test_count_missing_item_returns_zero(self):
        """Test counting an item not in inventory returns 0."""
        inv = Inventory()
        assert inv.count(MockItemKey.SWORD) == 0

    def test_count_after_adding(self):
        """Test count after adding items."""
        inv = Inventory()
        inv2 = inv + MockItemKey.POTION
        assert inv2.count(MockItemKey.POTION) == 1


class TestInventoryContains:
    """Tests for Inventory.__contains__ method."""

    def test_contains_single_item_key(self):
        """Test checking if a single item key is in inventory."""
        items = frozendict({MockItemKey.SWORD: 1})
        inv = Inventory(items=items)
        assert MockItemKey.SWORD in inv

    def test_not_contains_missing_item(self):
        """Test missing item is not in inventory."""
        inv = Inventory()
        assert MockItemKey.SWORD not in inv

    def test_contains_item_with_quantity(self):
        """Test checking if enough quantity is in inventory."""
        items = frozendict({MockItemKey.POTION: 5})
        inv = Inventory(items=items)
        assert MockItemKey.POTION * 3 in inv
        assert MockItemKey.POTION * 5 in inv

    def test_not_contains_insufficient_quantity(self):
        """Test insufficient quantity is not in inventory."""
        items = frozendict({MockItemKey.POTION: 2})
        inv = Inventory(items=items)
        assert MockItemKey.POTION * 3 not in inv

    def test_contains_multiple_items(self):
        """Test checking multiple items at once."""
        items = frozendict({MockItemKey.SWORD: 1, MockItemKey.POTION: 3})
        inv = Inventory(items=items)
        assert (MockItemKey.SWORD, MockItemKey.POTION * 2) in inv

    def test_not_contains_when_one_item_missing(self):
        """Test fails if any item in tuple is missing."""
        items = frozendict({MockItemKey.SWORD: 1})
        inv = Inventory(items=items)
        assert (MockItemKey.SWORD, MockItemKey.POTION) not in inv


class TestInventoryAddition:
    """Tests for Inventory.__add__ method."""

    def test_add_single_item_key(self):
        """Test adding a single item key increments count by 1."""
        inv = Inventory()
        inv2 = inv + MockItemKey.SWORD
        assert inv2.count(MockItemKey.SWORD) == 1

    def test_add_item_key_and_quantity(self):
        """Test adding an ItemKeyAndQuantity."""
        inv = Inventory()
        inv2 = inv + (MockItemKey.POTION * 5)
        assert inv2.count(MockItemKey.POTION) == 5

    def test_add_accumulates_existing_items(self):
        """Test adding to existing items accumulates."""
        items = frozendict({MockItemKey.SWORD: 2})
        inv = Inventory(items=items)
        inv2 = inv + MockItemKey.SWORD
        assert inv2.count(MockItemKey.SWORD) == 3

    def test_add_multiple_items_as_tuple(self):
        """Test adding multiple items via tuple."""
        inv = Inventory()
        inv2 = inv + (MockItemKey.SWORD, MockItemKey.POTION * 3)
        assert inv2.count(MockItemKey.SWORD) == 1
        assert inv2.count(MockItemKey.POTION) == 3

    def test_add_does_not_mutate_original(self):
        """Test that adding returns a new inventory without mutating the original."""
        inv = Inventory()
        _ = inv + MockItemKey.SWORD
        assert inv.count(MockItemKey.SWORD) == 0


class TestInventorySaveLoad:
    """Tests for Inventory save/load functionality."""

    def test_empty_inventory_save_data(self):
        """Test save data of empty inventory."""
        inv = Inventory()
        data = inv.save_data_this_class
        assert data == []

    def test_load_empty_inventory(self):
        """Test loading an empty inventory from save data."""
        inv = Inventory.load_this_class_from_save([])
        assert isinstance(inv, Inventory)
        assert len(inv.items) == 0
