"""Tests for nextrpg.geometry.direction module."""
import pytest
from nextrpg.geometry.direction import Direction


class TestDirectionEnum:
    """Tests for Direction enum values."""

    def test_all_directions_exist(self):
        """Test that all 8 directions are defined."""
        expected = {
            "DOWN", "LEFT", "RIGHT", "UP",
            "UP_LEFT", "UP_RIGHT", "DOWN_LEFT", "DOWN_RIGHT",
        }
        actual = {d.name for d in Direction}
        assert actual == expected

    def test_direction_count(self):
        """Test there are exactly 8 directions."""
        assert len(Direction) == 8


class TestDirectionOpposites:
    """Tests for Direction.__neg__ (opposite direction)."""

    def test_down_opposite_is_up(self):
        """Test DOWN opposite is UP."""
        assert -Direction.DOWN is Direction.UP

    def test_up_opposite_is_down(self):
        """Test UP opposite is DOWN."""
        assert -Direction.UP is Direction.DOWN

    def test_left_opposite_is_right(self):
        """Test LEFT opposite is RIGHT."""
        assert -Direction.LEFT is Direction.RIGHT

    def test_right_opposite_is_left(self):
        """Test RIGHT opposite is LEFT."""
        assert -Direction.RIGHT is Direction.LEFT

    def test_up_left_opposite_is_down_right(self):
        """Test UP_LEFT opposite is DOWN_RIGHT."""
        assert -Direction.UP_LEFT is Direction.DOWN_RIGHT

    def test_up_right_opposite_is_down_left(self):
        """Test UP_RIGHT opposite is DOWN_LEFT."""
        assert -Direction.UP_RIGHT is Direction.DOWN_LEFT

    def test_down_left_opposite_is_up_right(self):
        """Test DOWN_LEFT opposite is UP_RIGHT."""
        assert -Direction.DOWN_LEFT is Direction.UP_RIGHT

    def test_down_right_opposite_is_up_left(self):
        """Test DOWN_RIGHT opposite is UP_LEFT."""
        assert -Direction.DOWN_RIGHT is Direction.UP_LEFT

    def test_double_negation_returns_original(self):
        """Test that negating twice returns the original direction."""
        for direction in Direction:
            assert -(-direction) is direction


class TestDirectionSaveLoad:
    """Tests for Direction save/load functionality."""

    def test_save_data_is_name(self):
        """Test save_data_this_class returns the direction name."""
        assert Direction.DOWN.save_data_this_class == "DOWN"
        assert Direction.UP_LEFT.save_data_this_class == "UP_LEFT"

    def test_load_from_save(self):
        """Test loading a direction from save data."""
        for direction in Direction:
            save_data = direction.save_data
            loaded = Direction.load_from_save(save_data)
            assert loaded is direction
