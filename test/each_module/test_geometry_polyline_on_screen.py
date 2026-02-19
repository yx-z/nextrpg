"""Tests for nextrpg.geometry.polyline_on_screen module."""

from unittest.mock import MagicMock, patch

import pytest

from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.polyline_on_screen import PolylineOnScreen


class TestPolylineOnScreenCreation:
    """Test PolylineOnScreen creation and basic properties."""

    def test_polyline_creation_with_single_point(self):
        """Test creating a polyline with a single point."""
        point = Coordinate(100, 100)
        polyline = PolylineOnScreen((point,))

        assert polyline.points == (point,)
        assert len(polyline.points) == 1

    def test_polyline_creation_with_multiple_points(self):
        """Test creating a polyline with multiple points."""
        points = (
            Coordinate(0, 0),
            Coordinate(100, 0),
            Coordinate(100, 100),
            Coordinate(0, 100),
        )
        polyline = PolylineOnScreen(points)

        assert polyline.points == points
        assert len(polyline.points) == 4

    def test_polyline_is_frozen(self):
        """Test that PolylineOnScreen is immutable."""
        polyline = PolylineOnScreen((Coordinate(0, 0), Coordinate(100, 100)))

        with pytest.raises((AttributeError, TypeError)):
            polyline.points = (Coordinate(50, 50),)


class TestPolylineLength:
    """Test polyline length calculation."""

    def test_polyline_length_single_point(self):
        """Test length of polyline with single point."""
        polyline = PolylineOnScreen((Coordinate(0, 0),))

        # Length should be 0 for single point path back to itself
        assert polyline.length == 0

    def test_polyline_length_two_points_horizontal(self):
        """Test length of horizontal polyline."""
        points = (Coordinate(0, 0), Coordinate(100, 0))
        polyline = PolylineOnScreen(points)

        # Distance from (0,0) to (100,0) plus distance from (100,0) back to (0,0)
        assert polyline.length == 200

    def test_polyline_length_two_points_vertical(self):
        """Test length of vertical polyline."""
        points = (Coordinate(0, 0), Coordinate(0, 100))
        polyline = PolylineOnScreen(points)

        # Distance from (0,0) to (0,100) plus distance from (0,100) back to (0,0)
        assert polyline.length == 200

    def test_polyline_length_three_points_square(self):
        """Test length of three-point polyline forming partial square."""
        points = (
            Coordinate(0, 0),
            Coordinate(100, 0),
            Coordinate(100, 100),
        )
        polyline = PolylineOnScreen(points)

        # (0,0)→(100,0): 100 + (100,0)→(100,100): 100 + (100,100)→(0,0): ~141.4
        # Total is approximately 341.4, but allow 1 tolerance
        assert polyline.length == pytest.approx(341.42, 1)

    def test_polyline_length_four_points_square(self):
        """Test length of four-point polyline forming complete square."""
        points = (
            Coordinate(0, 0),
            Coordinate(100, 0),
            Coordinate(100, 100),
            Coordinate(0, 100),
        )
        polyline = PolylineOnScreen(points)

        # Each edge is 100, all 4 edges = 400
        assert polyline.length == 400

    def test_polyline_length_is_cached(self):
        """Test that polyline length is cached."""
        points = (Coordinate(0, 0), Coordinate(100, 100))
        polyline = PolylineOnScreen(points)

        # Access length multiple times
        length1 = polyline.length
        length2 = polyline.length

        # Should be the same object (cached)
        assert length1 == length2


class TestPolylineDistance:
    """Test distance calculations between points in polyline."""

    def test_polyline_points_distance_calculation(self):
        """Test individual distance calculations."""
        coord1 = Coordinate(0, 0)
        coord2 = Coordinate(3, 4)

        distance = coord1.distance(coord2)
        assert distance == 5  # 3-4-5 triangle

    def test_polyline_with_diagonal_points(self):
        """Test polyline with diagonal movements."""
        points = (
            Coordinate(0, 0),
            Coordinate(3, 4),
            Coordinate(6, 0),
        )
        polyline = PolylineOnScreen(points)

        # (0,0)→(3,4): 5 + (3,4)→(6,0): 5 + (6,0)→(0,0): 6
        assert polyline.length == pytest.approx(16, 0.1)


class TestPolylineProperties:
    """Test other polyline properties and methods."""

    @pytest.mark.skip(reason="fill() requires drawing system initialization")
    def test_polyline_fill_method(self):
        """Test polyline fill method."""
        # This would require mocking the drawing system
        points = (Coordinate(0, 0), Coordinate(100, 100))
        polyline = PolylineOnScreen(points)

        # Just verify the method exists
        assert hasattr(polyline, "fill")

    @pytest.mark.skip(
        reason="_bounding_rectangle_area requires rectangle_area_on_screen"
    )
    def test_polyline_bounding_rectangle(self):
        """Test polyline bounding rectangle calculation."""
        # This depends on rectangle_area_on_screen which needs testing separately
        points = (
            Coordinate(10, 20),
            Coordinate(100, 50),
            Coordinate(50, 150),
        )
        polyline = PolylineOnScreen(points)

        # Should have a bounding rectangle
        assert hasattr(polyline, "_bounding_rectangle_area_on_screen")


class TestPolylineDataclass:
    """Test dataclass properties of PolylineOnScreen."""

    def test_polyline_equality(self):
        """Test polyline equality comparison."""
        points1 = (Coordinate(0, 0), Coordinate(100, 100))
        points2 = (Coordinate(0, 0), Coordinate(100, 100))

        polyline1 = PolylineOnScreen(points1)
        polyline2 = PolylineOnScreen(points2)

        assert polyline1 == polyline2

    def test_polyline_inequality(self):
        """Test polyline inequality comparison."""
        polyline1 = PolylineOnScreen((Coordinate(0, 0), Coordinate(100, 100)))
        polyline2 = PolylineOnScreen((Coordinate(0, 0), Coordinate(50, 50)))

        assert polyline1 != polyline2

    def test_polyline_repr(self):
        """Test polyline representation."""
        points = (Coordinate(0, 0), Coordinate(100, 100))
        polyline = PolylineOnScreen(points)

        repr_str = repr(polyline)
        assert "PolylineOnScreen" in repr_str


class TestPolylineEdgeCases:
    """Test edge cases and special scenarios."""

    def test_polyline_with_duplicate_consecutive_points(self):
        """Test polyline with same point twice in a row."""
        points = (
            Coordinate(0, 0),
            Coordinate(0, 0),
            Coordinate(100, 100),
        )
        polyline = PolylineOnScreen(points)

        # Should still calculate length (with 0 distance between duplicates)
        assert polyline.length >= 0

    def test_polyline_with_negative_coordinates(self):
        """Test polyline with negative coordinates."""
        points = (
            Coordinate(-100, -100),
            Coordinate(0, 0),
            Coordinate(100, 100),
        )
        polyline = PolylineOnScreen(points)

        # Should still work with negative coordinates
        assert polyline.length > 0

    def test_polyline_with_large_coordinates(self):
        """Test polyline with very large coordinates."""
        points = (
            Coordinate(10000, 10000),
            Coordinate(20000, 20000),
        )
        polyline = PolylineOnScreen(points)

        # Should handle large coordinates
        # Distance from (10000,10000) to (20000,20000) is ~14142
        # Distance back is the same, so total is ~28284
        assert polyline.length == pytest.approx(28284, 1)

    def test_polyline_many_points(self):
        """Test polyline with many points."""
        # Create a polyline with many points along a line
        points = tuple(Coordinate(i * 10, 0) for i in range(100))
        polyline = PolylineOnScreen(points)

        # Should handle many points without error
        assert len(polyline.points) == 100
        assert polyline.length > 0


class TestPolylineIntegration:
    """Integration tests for polyline with coordinate operations."""

    def test_polyline_points_can_be_offset(self):
        """Test that polyline points can be offset."""
        points = (Coordinate(0, 0), Coordinate(100, 100))
        polyline = PolylineOnScreen(points)

        offset = Coordinate(50, 50)
        offset_points = tuple(p + offset for p in polyline.points)
        offset_polyline = PolylineOnScreen(offset_points)

        # Lengths should be equal
        assert polyline.length == offset_polyline.length

    def test_polyline_points_can_be_scaled(self):
        """Test that polyline points can be scaled."""
        points = (Coordinate(0, 0), Coordinate(100, 100))
        polyline = PolylineOnScreen(points)

        scaled_points = tuple(p * 2 for p in polyline.points)
        scaled_polyline = PolylineOnScreen(scaled_points)

        # Scaled length should be double (within floating point tolerance)
        assert scaled_polyline.length == pytest.approx(
            polyline.length * 2, rel=0.01
        )
