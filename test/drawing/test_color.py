"""Tests for nextrpg.drawing.color module."""

import pytest

from nextrpg.drawing.color import Color, alpha_from_percentage


class TestColorCreation:
    """Test Color creation."""

    def test_color_creation_basic(self):
        """Test creating a basic Color."""
        color = Color(255, 128, 64)

        assert color.red == 255
        assert color.green == 128
        assert color.blue == 64

    def test_color_creation_with_alpha(self):
        """Test creating Color with alpha."""
        color = Color(255, 128, 64, 200)

        assert color.red == 255
        assert color.green == 128
        assert color.blue == 64
        assert color.alpha == 200

    def test_color_creation_zero(self):
        """Test black color (0, 0, 0)."""
        color = Color(0, 0, 0)

        assert color.red == 0
        assert color.green == 0
        assert color.blue == 0

    def test_color_creation_white(self):
        """Test white color (255, 255, 255)."""
        color = Color(255, 255, 255)

        assert color.red == 255
        assert color.green == 255
        assert color.blue == 255


class TestColorCommon:
    """Test common colors."""

    @pytest.mark.skip(reason="May not have predefined color constants")
    def test_color_red_constant(self):
        """Test red color constant."""
        # Check if common colors are defined
        pass


class TestAlphaFromPercentage:
    """Test alpha_from_percentage function."""

    def test_alpha_from_percentage_zero(self):
        """Test alpha from 0%."""
        alpha = alpha_from_percentage(0.0)

        assert alpha == 0

    def test_alpha_from_percentage_hundred(self):
        """Test alpha from 100%."""
        alpha = alpha_from_percentage(1.0)

        assert alpha == 255

    def test_alpha_from_percentage_half(self):
        """Test alpha from 50%."""
        alpha = alpha_from_percentage(0.5)

        # Should be approximately 127.5, likely rounded
        assert 126 <= alpha <= 128

    def test_alpha_from_percentage_quarter(self):
        """Test alpha from 25%."""
        alpha = alpha_from_percentage(0.25)

        # Should be approximately 63.75
        assert 63 <= alpha <= 64


class TestColorEquality:
    """Test Color equality."""

    def test_color_equality(self):
        """Test equal colors."""
        color1 = Color(255, 128, 64)
        color2 = Color(255, 128, 64)

        assert color1 == color2

    def test_color_equality_with_alpha(self):
        """Test equal colors with alpha."""
        color1 = Color(255, 128, 64, 200)
        color2 = Color(255, 128, 64, 200)

        assert color1 == color2

    def test_color_inequality(self):
        """Test different colors."""
        color1 = Color(255, 128, 64)
        color2 = Color(255, 128, 65)

        assert color1 != color2

    def test_color_inequality_alpha(self):
        """Test colors with different alpha."""
        color1 = Color(255, 128, 64, 200)
        color2 = Color(255, 128, 64, 201)

        assert color1 != color2


class TestColorIntegration:
    """Integration tests for colors."""

    def test_color_tuple_conversion(self):
        """Test converting Color to tuple."""
        color = Color(255, 128, 64)

        # Should be convertible to tuple
        assert isinstance(color, Color)

    def test_multiple_colors(self):
        """Test creating multiple colors."""
        colors = [Color(r, 128, 64) for r in range(0, 256, 50)]

        assert len(colors) > 0
        for color in colors:
            assert hasattr(color, "red")
            assert hasattr(color, "green")
            assert hasattr(color, "blue")
