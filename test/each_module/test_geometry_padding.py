"""
Tests for nextrpg.geometry module - padding and anchored coordinate.
"""

import pytest
from nextrpg.geometry.padding import Padding
from nextrpg.geometry.size import Height, Width, Size, ZERO_HEIGHT, ZERO_WIDTH
from nextrpg.geometry.coordinate import Coordinate


class TestPadding:
    """Tests for Padding class."""
    
    def test_padding_creation_defaults(self):
        """Test creating Padding with defaults."""
        padding = Padding()
        
        assert padding.top == ZERO_HEIGHT
        assert padding.left == ZERO_WIDTH
        assert padding.bottom == ZERO_HEIGHT
        assert padding.right == ZERO_WIDTH
    
    def test_padding_creation_custom(self):
        """Test creating Padding with custom values."""
        padding = Padding(
            top=Height(10),
            left=Width(5),
            bottom=Height(15),
            right=Width(20)
        )
        
        assert padding.top.value == 10
        assert padding.left.value == 5
        assert padding.bottom.value == 15
        assert padding.right.value == 20
    
    def test_padding_negation(self):
        """Test negating padding."""
        padding = Padding(
            top=Height(10),
            left=Width(5),
            bottom=Height(15),
            right=Width(20)
        )
        
        neg_padding = -padding
        
        assert neg_padding.top.value == -10
        assert neg_padding.left.value == -5
        assert neg_padding.bottom.value == -15
        assert neg_padding.right.value == -20
    
    def test_padding_double_negation(self):
        """Test that double negation returns original values."""
        padding = Padding(
            top=Height(10),
            left=Width(5),
            bottom=Height(15),
            right=Width(20)
        )
        
        double_neg = -(-padding)
        
        assert double_neg.top.value == padding.top.value
        assert double_neg.left.value == padding.left.value
        assert double_neg.bottom.value == padding.bottom.value
        assert double_neg.right.value == padding.right.value
    
    def test_padding_addition_with_padding(self):
        """Test adding two paddings."""
        padding1 = Padding(
            top=Height(5),
            left=Width(3),
            bottom=Height(4),
            right=Width(2)
        )
        padding2 = Padding(
            top=Height(2),
            left=Width(1),
            bottom=Height(3),
            right=Width(1)
        )
        
        result = padding1 + padding2
        
        assert isinstance(result, Padding)
        assert result.top.value == 7
        assert result.left.value == 4
        assert result.bottom.value == 7
        assert result.right.value == 3
    
    def test_padding_addition_with_size(self):
        """Test adding padding with size."""
        padding = Padding(
            top=Height(5),
            left=Width(10),
            bottom=Height(5),
            right=Width(10)
        )
        size = Size(100, 200)
        
        result = padding + size
        
        assert isinstance(result, Size)
        # width = left + size.width + right = 10 + 100 + 10 = 120
        assert result.width_value == 120
        # height = top + size.height + bottom = 5 + 200 + 5 = 210
        assert result.height_value == 210
    
    def test_padding_subtraction_with_padding(self):
        """Test subtracting two paddings."""
        padding1 = Padding(
            top=Height(10),
            left=Width(8),
            bottom=Height(6),
            right=Width(4)
        )
        padding2 = Padding(
            top=Height(2),
            left=Width(1),
            bottom=Height(3),
            right=Width(1)
        )
        
        result = padding1 - padding2
        
        assert isinstance(result, Padding)
        assert result.top.value == 8
        assert result.left.value == 7
        assert result.bottom.value == 3
        assert result.right.value == 3
    
    def test_padding_frozen(self):
        """Test Padding is frozen."""
        padding = Padding(top=Height(10))
        
        with pytest.raises(Exception):  # FrozenInstanceError
            padding.top = Height(20)
    
    def test_padding_horizontal_total(self):
        """Test total horizontal padding."""
        padding = Padding(
            left=Width(10),
            right=Width(15)
        )
        
        total_h = padding.left.value + padding.right.value
        assert total_h == 25
    
    def test_padding_vertical_total(self):
        """Test total vertical padding."""
        padding = Padding(
            top=Height(5),
            bottom=Height(10)
        )
        
        total_v = padding.top.value + padding.bottom.value
        assert total_v == 15
    
    def test_padding_with_size_subtraction(self):
        """Test subtracting padding from size."""
        padding = Padding(
            top=Height(5),
            left=Width(10),
            bottom=Height(5),
            right=Width(10)
        )
        size = Size(130, 220)
        
        # size - padding should remove the padding
        result = size - padding
        
        assert isinstance(result, Size)
        # width = size.width - left - right = 130 - 10 - 10 = 110
        assert result.width_value == 110
        # height = size.height - top - bottom = 220 - 5 - 5 = 210
        assert result.height_value == 210


class TestPaddingIntegration:
    """Integration tests for Padding."""
    
    def test_padding_symmetric(self):
        """Test creating symmetric padding."""
        padding = Padding(
            top=Height(10),
            left=Width(10),
            bottom=Height(10),
            right=Width(10)
        )
        
        assert padding.top == padding.bottom
        assert padding.left == padding.right
    
    def test_padding_with_size_formula(self):
        """Test padding + size formula."""
        padding = Padding(
            top=Height(2),
            left=Width(3),
            bottom=Height(4),
            right=Width(5)
        )
        size = Size(100, 200)
        
        padded = padding + size
        
        expected_width = 3 + 100 + 5
        expected_height = 2 + 200 + 4
        
        assert padded.width_value == expected_width
        assert padded.height_value == expected_height
    
    def test_zero_padding(self):
        """Test zero padding."""
        zero_padding = Padding()
        size = Size(100, 200)
        
        result = zero_padding + size
        
        assert result.width_value == 100
        assert result.height_value == 200
    
    def test_padding_cancellation(self):
        """Test that padding + (-padding) * 2 works."""
        padding = Padding(
            top=Height(5),
            left=Width(10),
            bottom=Height(5),
            right=Width(10)
        )
        
        double_neg = padding + (-padding)
        
        # This should give us zero padding
        assert double_neg.top.value == 0
        assert double_neg.left.value == 0
        assert double_neg.bottom.value == 0
        assert double_neg.right.value == 0


class TestAnchoredCoordinate:
    """Tests for anchored coordinate functionality."""
    
    def test_coordinate_with_anchor_top_left(self):
        """Test coordinate with top left anchor."""
        from nextrpg.geometry.anchor import Anchor
        
        coord = Coordinate(100, 50)
        size = Size(200, 100)
        
        anchored = coord.as_top_left_of(size)
        
        # Should have the coordinate as top left
        assert hasattr(anchored, 'top_left')
    
    def test_coordinate_with_anchor_center(self):
        """Test coordinate with center anchor."""
        from nextrpg.geometry.anchor import Anchor
        
        coord = Coordinate(150, 150)
        size = Size(200, 100)
        
        anchored = coord.as_center_of(size)
        
        # Should have coordinate as center point
        assert hasattr(anchored, 'center')
    
    def test_coordinate_as_anchor_method(self):
        """Test as_anchor_of method."""
        from nextrpg.geometry.anchor import Anchor
        
        coord = Coordinate(100, 100)
        size = Size(200, 200)
        
        # Should work with all anchor types
        for anchor in Anchor:
            result = coord.as_anchor_of(size, anchor)
            assert result is not None


class TestPaddingEdgeCases:
    """Tests for edge cases in Padding."""
    
    def test_padding_all_zero(self):
        """Test padding with all zero values."""
        padding = Padding(
            top=Height(0),
            left=Width(0),
            bottom=Height(0),
            right=Width(0)
        )
        
        size = Size(100, 200)
        result = padding + size
        
        assert result.width_value == 100
        assert result.height_value == 200
    
    def test_padding_large_values(self):
        """Test padding with large values."""
        padding = Padding(
            top=Height(1000),
            left=Width(2000),
            bottom=Height(3000),
            right=Width(4000)
        )
        
        size = Size(100, 200)
        result = padding + size
        
        assert result.width_value == 6100
        assert result.height_value == 4200
    
    def test_padding_float_values(self):
        """Test padding with float values."""
        padding = Padding(
            top=Height(10.5),
            left=Width(5.5),
            bottom=Height(12.5),
            right=Width(7.5)
        )
        
        size = Size(100, 200)
        result = padding + size
        
        assert result.width_value == 113.0
        assert result.height_value == 223.0
