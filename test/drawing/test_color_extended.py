"""Extended tests for nextrpg.drawing.color module."""
import pytest
from nextrpg.drawing.color import (
    Color,
    alpha_from_percentage,
    RED,
    GREEN,
    BLUE,
    BLACK,
    WHITE,
    TRANSPARENT,
)


class TestColorConstants:
    """Tests for predefined color constants."""

    def test_red_constant(self):
        """Test RED constant has correct values."""
        assert RED.red == 255
        assert RED.green == 0
        assert RED.blue == 0
        assert RED.alpha == 255

    def test_green_constant(self):
        """Test GREEN constant has correct values."""
        assert GREEN.red == 0
        assert GREEN.green == 255
        assert GREEN.blue == 0
        assert GREEN.alpha == 255

    def test_blue_constant(self):
        """Test BLUE constant has correct values."""
        assert BLUE.red == 0
        assert BLUE.green == 0
        assert BLUE.blue == 255
        assert BLUE.alpha == 255

    def test_black_constant(self):
        """Test BLACK constant has correct values."""
        assert BLACK.red == 0
        assert BLACK.green == 0
        assert BLACK.blue == 0
        assert BLACK.alpha == 255

    def test_white_constant(self):
        """Test WHITE constant has correct values."""
        assert WHITE.red == 255
        assert WHITE.green == 255
        assert WHITE.blue == 255
        assert WHITE.alpha == 255

    def test_transparent_constant(self):
        """Test TRANSPARENT constant has zero alpha."""
        assert TRANSPARENT.alpha == 0


class TestColorWithAlpha:
    """Tests for Color.with_alpha and with_percentage_alpha."""

    def test_with_alpha_creates_new_color(self):
        """Test with_alpha returns a new Color with the given alpha."""
        color = Color(255, 0, 0)
        new_color = color.with_alpha(128)
        assert new_color.red == 255
        assert new_color.green == 0
        assert new_color.blue == 0
        assert new_color.alpha == 128

    def test_with_alpha_does_not_mutate_original(self):
        """Test with_alpha does not change the original color."""
        color = Color(255, 0, 0)
        _ = color.with_alpha(128)
        assert color.alpha == 255

    def test_with_percentage_alpha_full(self):
        """Test with_percentage_alpha at 100% gives alpha=255."""
        color = Color(255, 0, 0)
        new_color = color.with_percentage_alpha(1.0)
        assert new_color.alpha == 255

    def test_with_percentage_alpha_zero(self):
        """Test with_percentage_alpha at 0% gives alpha=0."""
        color = Color(255, 0, 0)
        new_color = color.with_percentage_alpha(0.0)
        assert new_color.alpha == 0

    def test_with_percentage_alpha_half(self):
        """Test with_percentage_alpha at 50% gives alpha~127."""
        color = Color(255, 0, 0)
        new_color = color.with_percentage_alpha(0.5)
        assert 126 <= new_color.alpha <= 128


class TestColorPygame:
    """Tests for Color.pygame property."""

    def test_pygame_returns_tuple(self):
        """Test pygame property returns a tuple of 4 ints."""
        color = Color(100, 150, 200, 255)
        pg = color.pygame
        assert pg == (100, 150, 200, 255)
        assert isinstance(pg, tuple)
        assert len(pg) == 4


class TestColorSaveLoad:
    """Tests for Color save/load round-trip."""

    def test_save_data_is_tuple(self):
        """Test save_data_this_class returns a tuple."""
        color = Color(10, 20, 30, 40)
        data = color.save_data_this_class
        assert data == (10, 20, 30, 40)

    def test_load_from_save_round_trip(self):
        """Test loading a color from its save data."""
        original = Color(50, 100, 150, 200)
        save_data = original.save_data
        loaded = Color.load_from_save(save_data)
        assert loaded == original

    def test_load_from_save_invalid_length(self):
        """Test loading from invalid data raises AssertionError."""
        invalid_data = {"class": ("nextrpg.drawing.color", "Color"), "save_data": [1, 2, 3]}
        with pytest.raises(AssertionError):
            Color.load_from_save(invalid_data)


class TestAlphaFromPercentageClamping:
    """Tests for alpha_from_percentage clamping behavior."""

    def test_clamp_above_one(self):
        """Test values above 1.0 are clamped to 255."""
        assert alpha_from_percentage(2.0) == 255

    def test_clamp_below_zero(self):
        """Test values below 0.0 are clamped to 0."""
        assert alpha_from_percentage(-0.5) == 0

    def test_exact_zero(self):
        """Test exactly 0.0 gives 0."""
        assert alpha_from_percentage(0.0) == 0

    def test_exact_one(self):
        """Test exactly 1.0 gives 255."""
        assert alpha_from_percentage(1.0) == 255

    def test_quarter(self):
        """Test 0.25 gives approximately 63."""
        result = alpha_from_percentage(0.25)
        assert 63 <= result <= 64
