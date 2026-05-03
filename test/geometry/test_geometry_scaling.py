"""Tests for nextrpg.geometry.scaling module."""
import pytest
from nextrpg.geometry.scaling import (
    Scaling,
    WidthScaling,
    HeightScaling,
    WidthAndHeightScaling,
)
from nextrpg.geometry.size import Width, Height, Size


class TestScaling:
    """Tests for the base Scaling class."""

    def test_scaling_creation(self):
        """Test creating a Scaling instance via WidthScaling."""
        s = WidthScaling(0.5)
        assert s.value == 0.5

    def test_scaling_complement_of_half(self):
        """Test complement of 0.5 is 0.5."""
        s = WidthScaling(0.5)
        assert s.complement.value == pytest.approx(0.5)

    def test_scaling_complement_of_zero(self):
        """Test complement of 0.0 is 1.0."""
        s = WidthScaling(0.0)
        assert s.complement.value == pytest.approx(1.0)

    def test_scaling_complement_of_one(self):
        """Test complement of 1.0 is 0.0."""
        s = WidthScaling(1.0)
        assert s.complement.value == pytest.approx(0.0)

    def test_scaling_complement_type_preserved(self):
        """Test complement preserves the type."""
        ws = WidthScaling(0.3)
        assert isinstance(ws.complement, WidthScaling)

        hs = HeightScaling(0.7)
        assert isinstance(hs.complement, HeightScaling)


class TestWidthScaling:
    """Tests for WidthScaling class."""

    def test_width_scaling_multiply_by_scalar(self):
        """Test WidthScaling * scalar returns WidthScaling."""
        ws = WidthScaling(2.0)
        result = ws * 3.0
        assert isinstance(result, WidthScaling)
        assert result.value == pytest.approx(6.0)

    def test_width_scaling_multiply_by_width(self):
        """Test WidthScaling * Width returns Width."""
        ws = WidthScaling(2.0)
        w = Width(50)
        result = ws * w
        assert isinstance(result, Width)
        assert result.value == pytest.approx(100.0)

    def test_width_scaling_half(self):
        """Test halving a Width via WidthScaling."""
        ws = WidthScaling(0.5)
        w = Width(100)
        result = ws * w
        assert result.value == pytest.approx(50.0)


class TestHeightScaling:
    """Tests for HeightScaling class."""

    def test_height_scaling_multiply_by_scalar(self):
        """Test HeightScaling * scalar returns HeightScaling."""
        hs = HeightScaling(3.0)
        result = hs * 2.0
        assert isinstance(result, HeightScaling)
        assert result.value == pytest.approx(6.0)

    def test_height_scaling_multiply_by_height(self):
        """Test HeightScaling * Height returns Height."""
        hs = HeightScaling(2.0)
        h = Height(75)
        result = hs * h
        assert isinstance(result, Height)
        assert result.value == pytest.approx(150.0)


class TestWidthAndHeightScaling:
    """Tests for WidthAndHeightScaling class."""

    def test_wah_scaling_multiply_by_scalar(self):
        """Test WidthAndHeightScaling * scalar returns WidthAndHeightScaling."""
        s = WidthAndHeightScaling(2.0)
        result = s * 3.0
        assert isinstance(result, WidthAndHeightScaling)
        assert result.value == pytest.approx(6.0)

    def test_wah_scaling_multiply_by_size(self):
        """Test WidthAndHeightScaling * Size returns Size."""
        s = WidthAndHeightScaling(2.0)
        size = Size(100, 200)
        result = s * size
        assert isinstance(result, Size)
        assert result.width_value == pytest.approx(200.0)
        assert result.height_value == pytest.approx(400.0)

    def test_wah_scaling_half_size(self):
        """Test halving a Size via WidthAndHeightScaling."""
        s = WidthAndHeightScaling(0.5)
        size = Size(80, 60)
        result = s * size
        assert result.width_value == pytest.approx(40.0)
        assert result.height_value == pytest.approx(30.0)
