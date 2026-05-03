"""Extended tests for nextrpg.item.item module."""
import pytest
from enum import auto
from nextrpg.item.item import Item
from nextrpg.config.rpg.item_config import BaseItemKey, ItemCategory


class MockItemKey(BaseItemKey):
    SWORD = auto()
    POTION = auto()
    SHIELD = auto()


class TestItemCreation:
    """Tests for Item creation."""

    def test_basic_item_creation(self):
        """Test creating a basic item with key and name."""
        item = Item(key=MockItemKey.SWORD, name="Iron Sword")
        assert item.key is MockItemKey.SWORD
        assert item.name == "Iron Sword"

    def test_item_default_description(self):
        """Test item has empty description by default."""
        item = Item(key=MockItemKey.SWORD, name="Iron Sword")
        assert item.description == ""

    def test_item_custom_description(self):
        """Test item with custom description."""
        item = Item(
            key=MockItemKey.SWORD,
            name="Iron Sword",
            description="A sturdy iron sword.",
        )
        assert item.description == "A sturdy iron sword."

    def test_item_default_category(self):
        """Test item has GENERIC category by default."""
        item = Item(key=MockItemKey.SWORD, name="Iron Sword")
        assert item.category is ItemCategory.GENERIC

    def test_item_custom_category(self):
        """Test item with custom category."""
        item = Item(
            key=MockItemKey.SWORD,
            name="Iron Sword",
            category=ItemCategory.WEAPON,
        )
        assert item.category is ItemCategory.WEAPON

    def test_item_is_frozen(self):
        """Test item is immutable."""
        item = Item(key=MockItemKey.SWORD, name="Iron Sword")
        with pytest.raises(Exception):
            item.name = "Steel Sword"


class TestItemEquality:
    """Tests for Item equality."""

    def test_items_with_same_key_are_equal(self):
        """Test items with the same key are equal."""
        item1 = Item(key=MockItemKey.SWORD, name="Iron Sword")
        item2 = Item(key=MockItemKey.SWORD, name="Steel Sword")
        assert item1 == item2

    def test_items_with_different_keys_are_not_equal(self):
        """Test items with different keys are not equal."""
        item1 = Item(key=MockItemKey.SWORD, name="Iron Sword")
        item2 = Item(key=MockItemKey.POTION, name="Health Potion")
        assert item1 != item2


class TestItemIcon:
    """Tests for Item.icon property."""

    def test_item_icon_none_by_default(self):
        """Test item icon is None when no icon_input is provided."""
        item = Item(key=MockItemKey.SWORD, name="Iron Sword")
        # icon returns None when no icon_input and no config icon
        # (config().rpg.item.icons.get(category) returns None by default)
        icon = item.icon
        assert icon is None

    def test_item_icon_with_callable(self):
        """Test item icon with callable icon_input."""
        mock_sprite = object()
        item = Item(
            key=MockItemKey.SWORD,
            name="Iron Sword",
            icon_input=lambda: mock_sprite,
        )
        assert item.icon is mock_sprite

    def test_item_icon_with_direct_sprite(self):
        """Test item icon with direct sprite icon_input."""
        mock_sprite = object()
        item = Item(
            key=MockItemKey.SWORD,
            name="Iron Sword",
            icon_input=mock_sprite,
        )
        assert item.icon is mock_sprite


class TestItemKeyAndQuantity:
    """Tests for BaseItemKey multiplication."""

    def test_multiply_key_by_quantity(self):
        """Test multiplying a key by a quantity."""
        result = MockItemKey.SWORD * 3
        assert result.key is MockItemKey.SWORD
        assert result.quantity == 3

    def test_reverse_multiply(self):
        """Test reverse multiplication."""
        result = 5 * MockItemKey.POTION
        assert result.key is MockItemKey.POTION
        assert result.quantity == 5

    def test_negate_key(self):
        """Test negating a key gives quantity -1."""
        result = -MockItemKey.SWORD
        assert result.key is MockItemKey.SWORD
        assert result.quantity == -1

    def test_positive_key(self):
        """Test +key gives quantity 1."""
        result = +MockItemKey.POTION
        assert result.key is MockItemKey.POTION
        assert result.quantity == 1

    def test_item_key_and_quantity_tuple(self):
        """Test ItemKeyAndQuantity.tuple property."""
        kq = MockItemKey.SWORD * 7
        t = kq.tuple
        assert t == (MockItemKey.SWORD, 7)
