"""
Tests for nextrpg.geometry.coordinate module.
"""

import pytest
import math
from nextrpg.geometry.coordinate import Coordinate, XAxis, YAxis, ORIGIN
from nextrpg.geometry.direction import Direction


class TestXAxis:
    """Tests for XAxis class."""
    
    def test_xaxis_creation(self):
        """Test creating an XAxis instance."""
        axis = XAxis(100)
        assert axis.value == 100
    
    def test_xaxis_width_property(self):
        """Test XAxis.width property returns Width."""
        axis = XAxis(100)
        width = axis.width
        assert width.value == 100
    
    def test_xaxis_addition_with_pixel(self):
        """Test XAxis addition with pixel value."""
        axis = XAxis(50)
        result = axis + 30
        assert isinstance(result, XAxis)
        assert result.value == 80
    
    def test_xaxis_addition_with_width(self):
        """Test XAxis addition with Width."""
        from nextrpg.geometry.size import Width
        axis = XAxis(50)
        width = Width(30)
        result = axis + width
        assert isinstance(result, XAxis)
        assert result.value == 80
    
    def test_xaxis_subtraction_with_pixel(self):
        """Test XAxis subtraction with pixel value."""
        axis = XAxis(80)
        result = axis - 30
        assert isinstance(result, XAxis)
        assert result.value == 50
    
    def test_xaxis_subtraction_with_xaxis(self):
        """Test XAxis subtraction with another XAxis."""
        from nextrpg.geometry.size import Width
        axis1 = XAxis(80)
        axis2 = XAxis(30)
        result = axis1 - axis2
        assert isinstance(result, Width)
        assert result.value == 50
    
    def test_xaxis_matmul_with_yaxis(self):
        """Test XAxis @ YAxis creates Coordinate."""
        x = XAxis(100)
        y = YAxis(200)
        coord = x @ y
        assert isinstance(coord, Coordinate)
        assert coord.left_value == 100
        assert coord.top_value == 200
    
    def test_xaxis_coordinate_property(self):
        """Test XAxis.coordinate property."""
        axis = XAxis(100)
        coord = axis.coordinate
        assert isinstance(coord, Coordinate)
        assert coord.left_value == 100
        assert coord.top_value == 0


class TestYAxis:
    """Tests for YAxis class."""
    
    def test_yaxis_creation(self):
        """Test creating a YAxis instance."""
        axis = YAxis(200)
        assert axis.value == 200
    
    def test_yaxis_height_property(self):
        """Test YAxis.height property returns Height."""
        axis = YAxis(100)
        height = axis.height
        assert height.value == 100
    
    def test_yaxis_addition_with_pixel(self):
        """Test YAxis addition with pixel value."""
        axis = YAxis(50)
        result = axis + 30
        assert isinstance(result, YAxis)
        assert result.value == 80
    
    def test_yaxis_matmul_with_xaxis(self):
        """Test YAxis @ XAxis creates Coordinate."""
        x = XAxis(100)
        y = YAxis(200)
        coord = y @ x
        assert isinstance(coord, Coordinate)
        assert coord.left_value == 100
        assert coord.top_value == 200
    
    def test_yaxis_coordinate_property(self):
        """Test YAxis.coordinate property."""
        axis = YAxis(200)
        coord = axis.coordinate
        assert isinstance(coord, Coordinate)
        assert coord.left_value == 0
        assert coord.top_value == 200


class TestCoordinate:
    """Tests for Coordinate class."""
    
    def test_coordinate_creation(self):
        """Test creating a Coordinate."""
        coord = Coordinate(100, 200)
        assert coord.left_value == 100
        assert coord.top_value == 200
    
    def test_coordinate_left_property(self):
        """Test Coordinate.left returns XAxis."""
        coord = Coordinate(100, 200)
        left = coord.left
        assert isinstance(left, XAxis)
        assert left.value == 100
    
    def test_coordinate_top_property(self):
        """Test Coordinate.top returns YAxis."""
        coord = Coordinate(100, 200)
        top = coord.top
        assert isinstance(top, YAxis)
        assert top.value == 200
    
    def test_coordinate_coordinate_property(self):
        """Test Coordinate.coordinate returns self."""
        coord = Coordinate(100, 200)
        assert coord.coordinate is coord
    
    def test_coordinate_negation(self):
        """Test coordinate negation."""
        coord = Coordinate(100, 200)
        neg_coord = -coord
        assert neg_coord.left_value == -100
        assert neg_coord.top_value == -200
    
    def test_coordinate_multiplication(self):
        """Test coordinate multiplication by scalar."""
        coord = Coordinate(100, 200)
        result = coord * 2
        assert isinstance(result, Coordinate)
        assert result.left_value == 200
        assert result.top_value == 400
    
    def test_coordinate_reverse_multiplication(self):
        """Test scalar multiplication of coordinate."""
        coord = Coordinate(100, 200)
        result = 2 * coord
        assert isinstance(result, Coordinate)
        assert result.left_value == 200
        assert result.top_value == 400
    
    def test_coordinate_addition_with_coordinate(self):
        """Test coordinate addition with another coordinate."""
        coord1 = Coordinate(100, 200)
        coord2 = Coordinate(50, 75)
        result = coord1 + coord2
        assert isinstance(result, Coordinate)
        assert result.left_value == 150
        assert result.top_value == 275
    
    def test_coordinate_addition_with_width(self):
        """Test coordinate addition with Width."""
        from nextrpg.geometry.size import Width
        coord = Coordinate(100, 200)
        width = Width(50)
        result = coord + width
        assert isinstance(result, Coordinate)
        assert result.left_value == 150
        assert result.top_value == 200
    
    def test_coordinate_addition_with_height(self):
        """Test coordinate addition with Height."""
        from nextrpg.geometry.size import Height
        coord = Coordinate(100, 200)
        height = Height(75)
        result = coord + height
        assert isinstance(result, Coordinate)
        assert result.left_value == 100
        assert result.top_value == 275
    
    def test_coordinate_addition_with_size(self):
        """Test coordinate addition with Size."""
        from nextrpg.geometry.size import Size
        coord = Coordinate(100, 200)
        size = Size(50, 75)
        result = coord + size
        assert isinstance(result, Coordinate)
        assert result.left_value == 150
        assert result.top_value == 275
    
    def test_coordinate_subtraction(self):
        """Test coordinate subtraction."""
        coord1 = Coordinate(100, 200)
        coord2 = Coordinate(30, 50)
        result = coord1 - coord2
        assert isinstance(result, Coordinate)
        assert result.left_value == 70
        assert result.top_value == 150
    
    def test_coordinate_distance(self):
        """Test distance calculation between coordinates."""
        coord1 = Coordinate(0, 0)
        coord2 = Coordinate(3, 4)
        distance = coord1.distance(coord2)
        assert distance == 5  # 3-4-5 triangle
    
    def test_coordinate_distance_same_point(self):
        """Test distance from coordinate to itself."""
        coord = Coordinate(100, 200)
        distance = coord.distance(coord)
        assert distance == 0
    
    def test_coordinate_relative_to_direction(self):
        """Test relative_to method returns direction."""
        origin = Coordinate(0, 0)
        
        # Test right direction
        right = Coordinate(100, 0)
        assert origin.relative_to(right) == Direction.LEFT
        
        # Test up direction
        up = Coordinate(0, -100)
        assert origin.relative_to(up) == Direction.DOWN
    
    def test_coordinate_string_representation(self):
        """Test string representation of coordinate."""
        coord = Coordinate(100.5, 200.7)
        str_repr = str(coord)
        # Coordinates are rounded to nearest integer in string representation
        assert "100" in str_repr or "101" in str_repr
        assert "200" in str_repr or "201" in str_repr
    
    def test_coordinate_repr(self):
        """Test repr of coordinate."""
        coord = Coordinate(100, 200)
        repr_str = repr(coord)
        assert isinstance(repr_str, str)
    
    def test_coordinate_save_data(self):
        """Test save_data property."""
        coord = Coordinate(100, 200)
        assert coord.save_data == coord
    
    def test_coordinate_load_from_save(self):
        """Test load_from_save class method."""
        data = [100, 200]
        coord = Coordinate.load_from_save(data)
        assert coord.left_value == 100
        assert coord.top_value == 200
    
    def test_coordinate_load_from_save_invalid_length(self):
        """Test load_from_save with invalid data length."""
        data = [100, 200, 300]
        with pytest.raises(AssertionError):
            Coordinate.load_from_save(data)
    
    def test_coordinate_directional_offset(self):
        """Test directional_offset property."""
        coord = Coordinate(100, 0)  # Point to the right
        offset = coord.directional_offset
        
        # DirectionalOffset has degree and offset attributes
        assert hasattr(offset, 'degree')
        assert hasattr(offset, 'offset')
        # Offset should be the distance from origin (100)
        assert offset.offset == 100


class TestOrigin:
    """Tests for ORIGIN constant."""
    
    def test_origin_value(self):
        """Test ORIGIN is at (0, 0)."""
        assert ORIGIN.left_value == 0
        assert ORIGIN.top_value == 0
