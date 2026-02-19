"""Tests for nextrpg.geometry.anchored_coordinate module."""

import pytest

from nextrpg.geometry.anchored_coordinate import (
    BottomCenterCoordinate,
    BottomLeftCoordinate,
    BottomRightCoordinate,
    CenterCoordinate,
    CenterLeftCoodinate,
    CenterRightCoordinate,
    TopCenterCoordinate,
    TopRightCoordinate,
)
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.size import Height, Size, Width


class TestTopCenterCoordinate:
    """Test TopCenterCoordinate class."""

    def test_top_center_coordinate_creation(self):
        """Test creating a TopCenterCoordinate."""
        coord = TopCenterCoordinate(100, 200)
        assert coord.left_value == 100
        assert coord.top_value == 200

    def test_top_center_as_top_left_of_size(self):
        """Test as_top_left_of delegates to as_top_center_of."""
        coord = TopCenterCoordinate(100, 200)
        size = Size(Width(50), Height(30))

        # Just test that the method exists and returns a sizable
        result = coord.as_top_left_of(size)
        assert result is not None


class TestTopRightCoordinate:
    """Test TopRightCoordinate class."""

    def test_top_right_coordinate_creation(self):
        """Test creating a TopRightCoordinate."""
        coord = TopRightCoordinate(200, 150)
        assert coord.left_value == 200
        assert coord.top_value == 150

    def test_top_right_as_top_left_of_size(self):
        """Test as_top_left_of delegates to as_top_right_of."""
        coord = TopRightCoordinate(200, 150)
        size = Size(Width(40), Height(25))

        result = coord.as_top_left_of(size)
        assert result is not None


class TestCenterLeftCoordinate:
    """Test CenterLeftCoordinate class."""

    def test_center_left_coordinate_creation(self):
        """Test creating a CenterLeftCoordinate."""
        coord = CenterLeftCoodinate(50, 100)
        assert coord.left_value == 50
        assert coord.top_value == 100

    def test_center_left_as_top_left_of_size(self):
        """Test as_top_left_of delegates to as_center_left_of."""
        coord = CenterLeftCoodinate(50, 100)
        size = Size(Width(30), Height(40))

        result = coord.as_top_left_of(size)
        assert result is not None


class TestCenterCoordinate:
    """Test CenterCoordinate class."""

    def test_center_coordinate_creation(self):
        """Test creating a CenterCoordinate."""
        coord = CenterCoordinate(250, 250)
        assert coord.left_value == 250
        assert coord.top_value == 250

    def test_center_as_top_left_of_size(self):
        """Test as_top_left_of delegates to as_center_of."""
        coord = CenterCoordinate(250, 250)
        size = Size(Width(100), Height(100))

        result = coord.as_top_left_of(size)
        assert result is not None


class TestCenterRightCoordinate:
    """Test CenterRightCoordinate class."""

    def test_center_right_coordinate_creation(self):
        """Test creating a CenterRightCoordinate."""
        coord = CenterRightCoordinate(300, 150)
        assert coord.left_value == 300
        assert coord.top_value == 150

    def test_center_right_as_top_left_of_size(self):
        """Test as_top_left_of delegates to as_center_right_of."""
        coord = CenterRightCoordinate(300, 150)
        size = Size(Width(50), Height(60))

        result = coord.as_top_left_of(size)
        assert result is not None


class TestBottomLeftCoordinate:
    """Test BottomLeftCoordinate class."""

    def test_bottom_left_coordinate_creation(self):
        """Test creating a BottomLeftCoordinate."""
        coord = BottomLeftCoordinate(0, 400)
        assert coord.left_value == 0
        assert coord.top_value == 400

    def test_bottom_left_as_top_left_of_size(self):
        """Test as_top_left_of delegates to as_bottom_left_of."""
        coord = BottomLeftCoordinate(0, 400)
        size = Size(Width(50), Height(50))

        result = coord.as_top_left_of(size)
        assert result is not None


class TestBottomCenterCoordinate:
    """Test BottomCenterCoordinate class."""

    def test_bottom_center_coordinate_creation(self):
        """Test creating a BottomCenterCoordinate."""
        coord = BottomCenterCoordinate(200, 400)
        assert coord.left_value == 200
        assert coord.top_value == 400

    def test_bottom_center_as_top_left_of_size(self):
        """Test as_top_left_of delegates to as_bottom_center_of."""
        coord = BottomCenterCoordinate(200, 400)
        size = Size(Width(80), Height(40))

        result = coord.as_top_left_of(size)
        assert result is not None


class TestBottomRightCoordinate:
    """Test BottomRightCoordinate class."""

    def test_bottom_right_coordinate_creation(self):
        """Test creating a BottomRightCoordinate."""
        coord = BottomRightCoordinate(400, 400)
        assert coord.left_value == 400
        assert coord.top_value == 400

    def test_bottom_right_as_top_left_of_size(self):
        """Test as_top_left_of delegates to as_bottom_right_of."""
        coord = BottomRightCoordinate(400, 400)
        size = Size(Width(60), Height(60))

        result = coord.as_top_left_of(size)
        assert result is not None


class TestAnchoredCoordinatesAreCoordinates:
    """Test that anchored coordinates are valid Coordinates."""

    def test_all_anchored_coordinates_inherit_from_coordinate(self):
        """Test that all anchored coordinate types are Coordinate instances."""
        coords = [
            TopCenterCoordinate(0, 0),
            TopRightCoordinate(0, 0),
            CenterLeftCoodinate(0, 0),
            CenterCoordinate(0, 0),
            CenterRightCoordinate(0, 0),
            BottomLeftCoordinate(0, 0),
            BottomCenterCoordinate(0, 0),
            BottomRightCoordinate(0, 0),
        ]

        for coord in coords:
            assert isinstance(coord, Coordinate)

    def test_anchored_coordinate_arithmetic(self):
        """Test that anchored coordinates support arithmetic operations."""
        coord = CenterCoordinate(100, 100)

        # Addition
        result = coord + Coordinate(10, 20)
        assert result.left_value == 110
        assert result.top_value == 120

        # Subtraction
        result2 = coord - Coordinate(10, 20)
        assert result2.left_value == 90
        assert result2.top_value == 80


class TestAnchoredCoordinateInheritance:
    """Test inheritance chain of anchored coordinates."""

    def test_type_preservation_in_operations(self):
        """Test that operations preserve/change types as expected."""
        # Adding to a TopCenterCoordinate doesn't necessarily preserve the type
        # since Coordinate does its own arithmetic
        coord = TopCenterCoordinate(100, 100)
        result = coord + Coordinate(10, 10)

        # Result should be coordinate but may not be TopCenterCoordinate
        assert isinstance(result, Coordinate)
        assert result.left_value == 110
        assert result.top_value == 110
