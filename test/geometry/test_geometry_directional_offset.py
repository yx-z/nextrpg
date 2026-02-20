"""
Tests for nextrpg.geometry.directional_offset module.
"""

import math

import pytest

from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.direction import Direction
from nextrpg.geometry.directional_offset import DirectionalOffset
from nextrpg.geometry.size import Size


class TestDirectionalOffsetWithDirection:
    """Tests for DirectionalOffset with Direction enum."""

    def test_creation_with_direction(self):
        """Test creating DirectionalOffset with Direction."""
        offset = DirectionalOffset(Direction.RIGHT, 100)

        assert offset.direction == Direction.RIGHT
        assert offset.offset == 100

    def test_creation_with_degree(self):
        """Test creating DirectionalOffset with degree value."""
        offset = DirectionalOffset(45, 100)

        assert offset.direction == 45
        assert offset.offset == 100

    def test_directional_offset_property(self):
        """Test directional_offset property returns self."""
        offset = DirectionalOffset(Direction.UP, 50)

        assert offset.directional_offset is offset

    def test_direction_to_degree_right(self):
        """Test Direction.RIGHT converts to 0 degrees."""
        offset = DirectionalOffset(Direction.RIGHT, 100)

        assert offset.degree == 0

    def test_direction_to_degree_left(self):
        """Test Direction.LEFT converts to 180 degrees."""
        offset = DirectionalOffset(Direction.LEFT, 100)

        assert offset.degree == 180

    def test_direction_to_degree_up(self):
        """Test Direction.UP converts to 270 degrees."""
        offset = DirectionalOffset(Direction.UP, 100)

        assert offset.degree == 270

    def test_direction_to_degree_down(self):
        """Test Direction.DOWN converts to 90 degrees."""
        offset = DirectionalOffset(Direction.DOWN, 100)

        assert offset.degree == 90

    def test_direction_to_degree_diagonal(self):
        """Test Direction diagonal conversions."""
        assert DirectionalOffset(Direction.UP_LEFT, 100).degree == 225
        assert DirectionalOffset(Direction.UP_RIGHT, 100).degree == 315
        assert DirectionalOffset(Direction.DOWN_LEFT, 100).degree == 135
        assert DirectionalOffset(Direction.DOWN_RIGHT, 100).degree == 45

    def test_degree_property_with_numeric_degree(self):
        """Test degree property with numeric direction."""
        offset = DirectionalOffset(45, 100)

        assert offset.degree == 45

    def test_radian_conversion(self):
        """Test radian property converts degree correctly."""
        offset = DirectionalOffset(Direction.RIGHT, 100)

        expected_radian = math.radians(0)
        assert offset.radian == pytest.approx(expected_radian)

    def test_radian_90_degrees(self):
        """Test radian conversion for 90 degrees."""
        offset = DirectionalOffset(Direction.DOWN, 100)

        expected_radian = math.radians(90)
        assert offset.radian == pytest.approx(expected_radian)


class TestDirectionalOffsetCoordinate:
    """Tests for coordinate conversion in DirectionalOffset."""

    def test_size_calculation_right(self):
        """Test size calculation for right direction."""
        offset = DirectionalOffset(Direction.RIGHT, 100)
        size = offset.size

        # Right direction: width=100*cos(0)=100, height=100*sin(0)=0
        assert size.width_value == pytest.approx(100)
        assert size.height_value == pytest.approx(0)

    def test_size_calculation_down(self):
        """Test size calculation for down direction."""
        offset = DirectionalOffset(Direction.DOWN, 100)
        size = offset.size

        # Down (90 degrees): width=100*cos(90deg)≈0, height=100*sin(90deg)=100
        assert size.width_value == pytest.approx(0, abs=1e-10)
        assert size.height_value == pytest.approx(100)

    def test_size_calculation_up(self):
        """Test size calculation for up direction."""
        offset = DirectionalOffset(Direction.UP, 100)
        size = offset.size

        # Up (270 degrees): width=100*cos(270deg)≈0, height=100*sin(270deg)≈-100
        assert size.width_value == pytest.approx(0, abs=1e-10)
        assert size.height_value == pytest.approx(-100)

    def test_coordinate_property(self):
        """Test coordinate property."""
        offset = DirectionalOffset(Direction.RIGHT, 100)
        coord = offset.coordinate

        assert isinstance(coord, Coordinate)
        assert issubclass(type(coord), Coordinate)

    def test_coordinate_values_right(self):
        """Test coordinate values for right direction."""
        offset = DirectionalOffset(Direction.RIGHT, 100)
        coord = offset.coordinate

        assert coord.left_value == pytest.approx(100)
        assert coord.top_value == pytest.approx(0)


class TestDirectionalOffsetOperations:
    """Tests for operations on DirectionalOffset."""

    def test_multiplication_with_scalar(self):
        """Test multiplying DirectionalOffset by scalar."""
        offset = DirectionalOffset(Direction.RIGHT, 100)
        result = offset * 2

        assert isinstance(result, DirectionalOffset)
        assert result.direction == Direction.RIGHT
        assert result.offset == 200

    def test_reverse_multiplication(self):
        """Test scalar multiplication (reverse)."""
        offset = DirectionalOffset(Direction.RIGHT, 100)
        result = 2 * offset

        assert isinstance(result, DirectionalOffset)
        assert result.direction == Direction.RIGHT
        assert result.offset == 200

    def test_division_by_scalar(self):
        """Test dividing DirectionalOffset by scalar."""
        offset = DirectionalOffset(Direction.RIGHT, 100)
        result = offset / 2

        assert isinstance(result, DirectionalOffset)
        assert result.direction == Direction.RIGHT
        assert result.offset == 50

    def test_negation(self):
        """Test negating DirectionalOffset."""
        offset = DirectionalOffset(Direction.RIGHT, 100)
        neg_offset = -offset

        assert isinstance(neg_offset, DirectionalOffset)
        assert neg_offset.direction == Direction.RIGHT
        assert neg_offset.offset == -100

    def test_double_negation(self):
        """Test double negation."""
        offset = DirectionalOffset(Direction.RIGHT, 100)
        double_neg = -(-offset)

        assert double_neg.direction == offset.direction
        assert double_neg.offset == pytest.approx(offset.offset)


class TestDirectionalOffsetFrozen:
    """Tests for frozen behavior of DirectionalOffset."""

    def test_directional_offset_frozen(self):
        """Test DirectionalOffset is frozen."""
        offset = DirectionalOffset(Direction.RIGHT, 100)

        with pytest.raises(Exception):  # FrozenInstanceError
            offset.offset = 200


class TestDirectionalOffsetEdgeCases:
    """Tests for edge cases in DirectionalOffset."""

    def test_zero_offset(self):
        """Test DirectionalOffset with zero offset."""
        offset = DirectionalOffset(Direction.RIGHT, 0)

        assert offset.offset == 0
        assert offset.size.width_value == 0
        assert offset.size.height_value == 0

    def test_negative_offset(self):
        """Test DirectionalOffset with negative offset."""
        offset = DirectionalOffset(Direction.RIGHT, -100)

        assert offset.offset == -100
        # Negative offset should go opposite direction
        assert offset.size.width_value == pytest.approx(-100)

    def test_float_degrees(self):
        """Test DirectionalOffset with float degrees."""
        offset = DirectionalOffset(45.5, 100)

        assert offset.degree == 45.5
        expected_radian = math.radians(45.5)
        assert offset.radian == pytest.approx(expected_radian)

    def test_large_offset(self):
        """Test DirectionalOffset with large offset."""
        offset = DirectionalOffset(Direction.RIGHT, 10000)

        assert offset.offset == 10000
        assert offset.size.width_value == pytest.approx(10000)

    def test_float_offset(self):
        """Test DirectionalOffset with float offset."""
        offset = DirectionalOffset(Direction.RIGHT, 123.456)

        assert offset.offset == 123.456
        assert offset.size.width_value == pytest.approx(123.456)


class TestDirectionalOffsetIntegration:
    """Integration tests for DirectionalOffset."""

    def test_offset_magnitude(self):
        """Test calculating magnitude from offset."""
        offset = DirectionalOffset(Direction.RIGHT, 100)

        # Magnitude is just the offset value
        assert offset.offset == 100

    def test_diagonal_offset_45_degrees(self):
        """Test 45 degree diagonal offset."""
        offset = DirectionalOffset(Direction.DOWN_RIGHT, 100)
        size = offset.size

        # 45 degrees: width = 100*cos(45) ≈ 70.71, height = 100*sin(45) ≈ 70.71
        sqrt2_half = 1 / math.sqrt(2)
        assert size.width_value == pytest.approx(100 * sqrt2_half)
        assert size.height_value == pytest.approx(100 * sqrt2_half)

    def test_offset_composition(self):
        """Test composing multiple offsets."""
        offset1 = DirectionalOffset(Direction.RIGHT, 100)
        offset2 = DirectionalOffset(Direction.DOWN, 100)

        coord1 = offset1.coordinate
        coord2 = offset2.coordinate

        # Can compose coordinates from offsets
        combined = coord1 + coord2

        assert combined.left_value == pytest.approx(100)
        assert combined.top_value == pytest.approx(100)
