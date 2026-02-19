"""
Tests for nextrpg.geometry.size module.
"""

import pytest

from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.size import (
    ZERO_HEIGHT,
    ZERO_SIZE,
    ZERO_WIDTH,
    Height,
    Size,
    Width,
)


class TestWidth:
    """Tests for Width class."""

    def test_width_creation(self):
        """Test creating a Width instance."""
        width = Width(100)
        assert width.value == 100

    def test_width_x_axis_property(self):
        """Test Width.x_axis property returns XAxis."""
        from nextrpg.geometry.coordinate import XAxis

        width = Width(100)
        x_axis = width.x_axis
        assert isinstance(x_axis, XAxis)
        assert x_axis.value == 100

    def test_width_multiplication_with_height(self):
        """Test Width * Height returns Size."""
        width = Width(100)
        height = Height(200)
        result = width * height
        assert isinstance(result, Size)
        assert result.width_value == 100
        assert result.height_value == 200

    def test_width_multiplication_with_scalar(self):
        """Test Width * scalar returns Width."""
        width = Width(100)
        result = width * 2
        assert isinstance(result, Width)
        assert result.value == 200

    def test_width_division_with_width(self):
        """Test Width / Width returns WidthScaling."""
        from nextrpg.geometry.scaling import WidthScaling

        width1 = Width(200)
        width2 = Width(100)
        result = width1 / width2
        assert isinstance(result, WidthScaling)
        assert result.value == 2

    def test_width_division_with_scalar(self):
        """Test Width / scalar returns Width."""
        width = Width(100)
        result = width / 2
        assert isinstance(result, Width)
        assert result.value == 50

    def test_width_size_property(self):
        """Test Width.size property."""
        width = Width(100)
        size = width.size
        assert isinstance(size, Size)
        assert size.width_value == 100
        assert size.height_value == 0

    def test_width_addition_with_width(self):
        """Test Width + Width returns Width."""
        width1 = Width(100)
        width2 = Width(50)
        result = width1 + width2
        assert isinstance(result, Width)
        assert result.value == 150

    def test_width_addition_with_size(self):
        """Test Width + Size returns Size."""
        width = Width(100)
        size = Size(50, 200)
        result = width + size
        assert isinstance(result, Size)
        # Width adds to the width component
        assert result.width_value == 150
        assert result.height_value == 200

    def test_width_subtraction(self):
        """Test Width subtraction."""
        width1 = Width(100)
        width2 = Width(30)
        result = width1 - width2
        assert isinstance(result, Width)
        assert result.value == 70


class TestHeight:
    """Tests for Height class."""

    def test_height_creation(self):
        """Test creating a Height instance."""
        height = Height(200)
        assert height.value == 200

    def test_height_y_axis_property(self):
        """Test Height.y_axis property returns YAxis."""
        from nextrpg.geometry.coordinate import YAxis

        height = Height(200)
        y_axis = height.y_axis
        assert isinstance(y_axis, YAxis)
        assert y_axis.value == 200

    def test_height_multiplication_with_width(self):
        """Test Height * Width returns Size."""
        height = Height(200)
        width = Width(100)
        result = height * width
        assert isinstance(result, Size)
        assert result.width_value == 100
        assert result.height_value == 200

    def test_height_multiplication_with_scalar(self):
        """Test Height * scalar returns Height."""
        height = Height(200)
        result = height * 2
        assert isinstance(result, Height)
        assert result.value == 400

    def test_height_division_with_height(self):
        """Test Height / Height returns HeightScaling."""
        from nextrpg.geometry.scaling import HeightScaling

        height1 = Height(200)
        height2 = Height(100)
        result = height1 / height2
        assert isinstance(result, HeightScaling)
        assert result.value == 2

    def test_height_division_with_scalar(self):
        """Test Height / scalar returns Height."""
        height = Height(200)
        result = height / 2
        assert isinstance(result, Height)
        assert result.value == 100

    def test_height_size_property(self):
        """Test Height.size property."""
        height = Height(200)
        size = height.size
        assert isinstance(size, Size)
        assert size.width_value == 0
        assert size.height_value == 200

    def test_height_addition_with_height(self):
        """Test Height + Height returns Height."""
        height1 = Height(200)
        height2 = Height(50)
        result = height1 + height2
        assert isinstance(result, Height)
        assert result.value == 250

    def test_height_addition_with_size(self):
        """Test Height + Size returns Size."""
        height = Height(200)
        size = Size(100, 50)
        result = height + size
        assert isinstance(result, Size)
        assert result.width_value == 100
        # Height adds to the height component
        assert result.height_value == 250

    def test_height_subtraction(self):
        """Test Height subtraction."""
        height1 = Height(200)
        height2 = Height(30)
        result = height1 - height2
        assert isinstance(result, Height)
        assert result.value == 170


class TestSize:
    """Tests for Size class."""

    def test_size_creation(self):
        """Test creating a Size."""
        size = Size(100, 200)
        assert size.width_value == 100
        assert size.height_value == 200

    def test_size_property(self):
        """Test Size.size returns self."""
        size = Size(100, 200)
        assert size.size is size

    def test_size_width_property(self):
        """Test Size.width returns Width."""
        size = Size(100, 200)
        width = size.width
        assert isinstance(width, Width)
        assert width.value == 100

    def test_size_height_property(self):
        """Test Size.height returns Height."""
        size = Size(100, 200)
        height = size.height
        assert isinstance(height, Height)
        assert height.value == 200

    def test_size_negate_width(self):
        """Test Size.negate_width property."""
        size = Size(100, 200)
        result = size.negate_width
        assert result.width_value == -100
        assert result.height_value == 200

    def test_size_negate_height(self):
        """Test Size.negate_height property."""
        size = Size(100, 200)
        result = size.negate_height
        assert result.width_value == 100
        assert result.height_value == -200

    def test_size_negation(self):
        """Test Size negation."""
        size = Size(100, 200)
        result = -size
        assert result.width_value == -100
        assert result.height_value == -200

    def test_size_addition_with_size(self):
        """Test Size + Size returns Size."""
        size1 = Size(100, 200)
        size2 = Size(50, 75)
        result = size1 + size2
        assert isinstance(result, Size)
        assert result.width_value == 150
        assert result.height_value == 275

    def test_size_addition_with_width(self):
        """Test Size + Width returns Size."""
        size = Size(100, 200)
        width = Width(50)
        result = size + width
        assert isinstance(result, Size)
        assert result.width_value == 150
        assert result.height_value == 200

    def test_size_addition_with_height(self):
        """Test Size + Height returns Size."""
        size = Size(100, 200)
        height = Height(75)
        result = size + height
        assert isinstance(result, Size)
        assert result.width_value == 100
        assert result.height_value == 275

    def test_size_addition_with_coordinate(self):
        """Test Size + Coordinate returns Size."""
        size = Size(100, 200)
        coord = Coordinate(50, 75)
        result = size + coord
        assert isinstance(result, Size)
        assert result.width_value == 150
        assert result.height_value == 275

    def test_size_subtraction(self):
        """Test Size subtraction."""
        size1 = Size(100, 200)
        size2 = Size(30, 50)
        result = size1 - size2
        assert isinstance(result, Size)
        assert result.width_value == 70
        assert result.height_value == 150

    def test_size_multiplication_with_scalar(self):
        """Test Size * scalar returns Size."""
        size = Size(100, 200)
        result = size * 2
        assert isinstance(result, Size)
        assert result.width_value == 200
        assert result.height_value == 400

    def test_size_multiplication_with_width_scaling(self):
        """Test Size * WidthScaling returns Size."""
        from nextrpg.geometry.scaling import WidthScaling

        size = Size(100, 200)
        scaling = WidthScaling(2)
        result = size * scaling
        assert isinstance(result, Size)
        assert result.width_value == 200
        assert result.height_value == 200

    def test_size_multiplication_with_height_scaling(self):
        """Test Size * HeightScaling returns Size."""
        from nextrpg.geometry.scaling import HeightScaling

        size = Size(100, 200)
        scaling = HeightScaling(2)
        result = size * scaling
        assert isinstance(result, Size)
        assert result.width_value == 100
        assert result.height_value == 400

    def test_size_reverse_multiplication(self):
        """Test scalar * Size returns Size."""
        size = Size(100, 200)
        result = 2 * size
        assert isinstance(result, Size)
        assert result.width_value == 200
        assert result.height_value == 400

    def test_size_division(self):
        """Test Size division."""
        from nextrpg.geometry.scaling import WidthScaling

        size = Size(100, 200)
        scaling = WidthScaling(2)
        result = size / scaling
        assert isinstance(result, Size)
        assert result.width_value == 50
        assert result.height_value == 200

    def test_size_string_representation(self):
        """Test string representation."""
        size = Size(100, 200)
        str_repr = str(size)
        assert "100" in str_repr
        assert "200" in str_repr

    def test_size_repr(self):
        """Test repr."""
        size = Size(100, 200)
        repr_str = repr(size)
        assert isinstance(repr_str, str)

    def test_size_coordinate_property(self):
        """Test Size.coordinate property."""
        size = Size(100, 200)
        coord = size.coordinate
        assert isinstance(coord, Coordinate)
        assert coord.left_value == 100
        assert coord.top_value == 200

    def test_size_save_data(self):
        """Test save_data property."""
        size = Size(100, 200)
        assert size.save_data == size

    def test_size_load_from_save(self):
        """Test load_from_save class method."""
        data = [100, 200]
        size = Size.load_from_save(data)
        assert size.width_value == 100
        assert size.height_value == 200

    def test_size_load_from_save_invalid(self):
        """Test load_from_save with invalid data."""
        data = [100]
        with pytest.raises(AssertionError):
            Size.load_from_save(data)

    def test_size_directional_offset(self):
        """Test directional_offset property."""
        size = Size(100, 0)  # Width only
        offset = size.directional_offset

        # DirectionalOffset has degree and offset attributes
        assert hasattr(offset, "degree")
        assert hasattr(offset, "offset")
        # Offset should equal width when height is 0
        assert offset.offset == 100


class TestSizeConstants:
    """Tests for Size constants."""

    def test_zero_width(self):
        """Test ZERO_WIDTH constant."""
        assert ZERO_WIDTH.value == 0

    def test_zero_height(self):
        """Test ZERO_HEIGHT constant."""
        assert ZERO_HEIGHT.value == 0

    def test_zero_size(self):
        """Test ZERO_SIZE constant."""
        assert ZERO_SIZE.width_value == 0
        assert ZERO_SIZE.height_value == 0
