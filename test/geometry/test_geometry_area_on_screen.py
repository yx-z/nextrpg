"""Tests for nextrpg.geometry.area_on_screen module."""
import pytest
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.size import Size


class TestAreaOnScreenAbstractClass:
    """Tests for AreaOnScreen abstract class structure."""

    def test_area_on_screen_has_points_annotation(self):
        """Test AreaOnScreen has points annotation."""
        assert "points" in AreaOnScreen.__annotations__

    def test_area_on_screen_has_fill_method(self):
        """Test AreaOnScreen has fill abstract method."""
        assert "fill" in AreaOnScreen.__dict__

    def test_area_on_screen_has_collide_method(self):
        """Test AreaOnScreen has collide abstract method."""
        assert "collide" in AreaOnScreen.__dict__

    def test_area_on_screen_has_contains_method(self):
        """Test AreaOnScreen has __contains__ abstract method."""
        assert "__contains__" in AreaOnScreen.__dict__

    def test_area_on_screen_has_add_method(self):
        """Test AreaOnScreen has __add__ abstract method."""
        assert "__add__" in AreaOnScreen.__dict__

    def test_area_on_screen_has_sub_method(self):
        """Test AreaOnScreen has __sub__ method (concrete)."""
        assert "__sub__" in AreaOnScreen.__dict__

    def test_area_on_screen_is_abstract(self):
        """Test AreaOnScreen cannot be instantiated directly."""
        with pytest.raises(TypeError):
            AreaOnScreen()
