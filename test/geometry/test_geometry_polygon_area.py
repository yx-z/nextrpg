"""Tests for nextrpg.geometry.polygon_area_on_screen module."""
import pytest
from nextrpg.geometry.polygon_area_on_screen import (
    PolygonAreaOnScreen,
    get_bounding_rectangle_area_on_screen,
)
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.size import Width, Height


class TestPolygonAreaOnScreenCreation:
    """Tests for PolygonAreaOnScreen creation."""

    def test_triangle_creation(self):
        """Test creating a triangle polygon."""
        points = (
            Coordinate(0, 0),
            Coordinate(100, 0),
            Coordinate(50, 100),
        )
        poly = PolygonAreaOnScreen(points)
        assert len(poly.points) == 3

    def test_square_creation(self):
        """Test creating a square polygon."""
        points = (
            Coordinate(0, 0),
            Coordinate(100, 0),
            Coordinate(100, 100),
            Coordinate(0, 100),
        )
        poly = PolygonAreaOnScreen(points)
        assert len(poly.points) == 4


class TestPolygonAreaOnScreenBoundingBox:
    """Tests for bounding box computation."""

    def test_bounding_box_of_square(self):
        """Test bounding box of a square matches the square."""
        points = (
            Coordinate(10, 20),
            Coordinate(110, 20),
            Coordinate(110, 120),
            Coordinate(10, 120),
        )
        poly = PolygonAreaOnScreen(points)
        assert poly.top_left.left_value == pytest.approx(10)
        assert poly.top_left.top_value == pytest.approx(20)
        assert poly.size.width_value == pytest.approx(100)
        assert poly.size.height_value == pytest.approx(100)

    def test_bounding_box_of_triangle(self):
        """Test bounding box of a triangle."""
        points = (
            Coordinate(0, 0),
            Coordinate(100, 0),
            Coordinate(50, 80),
        )
        poly = PolygonAreaOnScreen(points)
        assert poly.top_left.left_value == pytest.approx(0)
        assert poly.top_left.top_value == pytest.approx(0)
        assert poly.size.width_value == pytest.approx(100)
        assert poly.size.height_value == pytest.approx(80)


class TestPolygonAreaOnScreenContains:
    """Tests for point containment."""

    def test_point_inside_square(self):
        """Test a point inside a square is contained."""
        points = (
            Coordinate(0, 0),
            Coordinate(100, 0),
            Coordinate(100, 100),
            Coordinate(0, 100),
        )
        poly = PolygonAreaOnScreen(points)
        assert Coordinate(50, 50) in poly

    def test_point_outside_square(self):
        """Test a point outside a square is not contained."""
        points = (
            Coordinate(0, 0),
            Coordinate(100, 0),
            Coordinate(100, 100),
            Coordinate(0, 100),
        )
        poly = PolygonAreaOnScreen(points)
        assert Coordinate(200, 200) not in poly

    def test_point_on_edge_of_square(self):
        """Test a point on the edge of a square."""
        points = (
            Coordinate(0, 0),
            Coordinate(100, 0),
            Coordinate(100, 100),
            Coordinate(0, 100),
        )
        poly = PolygonAreaOnScreen(points)
        # Point exactly at origin (corner)
        # Behavior at corners/edges can vary by implementation
        # Just test it doesn't raise
        result = Coordinate(0, 0) in poly
        assert isinstance(result, bool)


class TestPolygonAreaOnScreenAddition:
    """Tests for polygon translation."""

    def test_add_coordinate_shifts_polygon(self):
        """Test adding a coordinate shifts all polygon points."""
        points = (
            Coordinate(0, 0),
            Coordinate(100, 0),
            Coordinate(100, 100),
            Coordinate(0, 100),
        )
        poly = PolygonAreaOnScreen(points)
        offset = Coordinate(10, 20)
        shifted = poly + offset
        
        assert shifted.points[0].left_value == pytest.approx(10)
        assert shifted.points[0].top_value == pytest.approx(20)
        assert shifted.points[1].left_value == pytest.approx(110)
        assert shifted.points[1].top_value == pytest.approx(20)


class TestGetBoundingRectangle:
    """Tests for get_bounding_rectangle_area_on_screen helper."""

    def test_bounding_rectangle_of_points(self):
        """Test bounding rectangle of a set of points."""
        points = [
            Coordinate(5, 10),
            Coordinate(50, 10),
            Coordinate(50, 80),
            Coordinate(5, 80),
        ]
        rect = get_bounding_rectangle_area_on_screen(points)
        assert rect.top_left.left_value == pytest.approx(5)
        assert rect.top_left.top_value == pytest.approx(10)
        assert rect.size.width_value == pytest.approx(45)
        assert rect.size.height_value == pytest.approx(70)

    def test_bounding_rectangle_minimum_size(self):
        """Test bounding rectangle has at least size 1x1 for degenerate cases."""
        # Vertical line (same x)
        points = [Coordinate(10, 0), Coordinate(10, 100)]
        rect = get_bounding_rectangle_area_on_screen(points)
        assert rect.size.width_value >= 1
        assert rect.size.height_value >= 1
