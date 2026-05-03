"""Tests for nextrpg.geometry.anchor module."""
import pytest
from nextrpg.geometry.anchor import Anchor


class TestAnchorEnum:
    """Tests for Anchor enum values."""

    def test_anchor_has_all_positions(self):
        """Test that all 9 anchor positions are defined."""
        expected = {
            "TOP_LEFT", "TOP_CENTER", "TOP_RIGHT",
            "CENTER_LEFT", "CENTER", "CENTER_RIGHT",
            "BOTTOM_LEFT", "BOTTOM_CENTER", "BOTTOM_RIGHT",
        }
        actual = {a.name for a in Anchor}
        assert actual == expected

    def test_anchor_top_left_value(self):
        """Test TOP_LEFT anchor exists."""
        assert Anchor.TOP_LEFT is not None

    def test_anchor_center_value(self):
        """Test CENTER anchor exists."""
        assert Anchor.CENTER is not None

    def test_anchor_bottom_right_value(self):
        """Test BOTTOM_RIGHT anchor exists."""
        assert Anchor.BOTTOM_RIGHT is not None

    def test_anchor_count(self):
        """Test there are exactly 9 anchor positions."""
        assert len(Anchor) == 9


class TestAnchorOpposites:
    """Tests for Anchor opposite positions."""

    def test_top_left_opposite_is_bottom_right(self):
        """Test TOP_LEFT opposite is BOTTOM_RIGHT."""
        assert Anchor.TOP_LEFT.__neg__ is Anchor.BOTTOM_RIGHT

    def test_top_center_opposite_is_bottom_center(self):
        """Test TOP_CENTER opposite is BOTTOM_CENTER."""
        assert Anchor.TOP_CENTER.__neg__ is Anchor.BOTTOM_CENTER

    def test_top_right_opposite_is_bottom_left(self):
        """Test TOP_RIGHT opposite is BOTTOM_LEFT."""
        assert Anchor.TOP_RIGHT.__neg__ is Anchor.BOTTOM_LEFT

    def test_center_left_opposite_is_center_right(self):
        """Test CENTER_LEFT opposite is CENTER_RIGHT."""
        assert Anchor.CENTER_LEFT.__neg__ is Anchor.CENTER_RIGHT

    def test_center_opposite_is_center(self):
        """Test CENTER opposite is CENTER (self-opposite)."""
        assert Anchor.CENTER.__neg__ is Anchor.CENTER

    def test_center_right_opposite_is_center_left(self):
        """Test CENTER_RIGHT opposite is CENTER_LEFT."""
        assert Anchor.CENTER_RIGHT.__neg__ is Anchor.CENTER_LEFT

    def test_bottom_left_opposite_is_top_right(self):
        """Test BOTTOM_LEFT opposite is TOP_RIGHT."""
        assert Anchor.BOTTOM_LEFT.__neg__ is Anchor.TOP_RIGHT

    def test_bottom_center_opposite_is_top_center(self):
        """Test BOTTOM_CENTER opposite is TOP_CENTER."""
        assert Anchor.BOTTOM_CENTER.__neg__ is Anchor.TOP_CENTER

    def test_bottom_right_opposite_is_top_left(self):
        """Test BOTTOM_RIGHT opposite is TOP_LEFT."""
        assert Anchor.BOTTOM_RIGHT.__neg__ is Anchor.TOP_LEFT

    def test_opposite_is_symmetric(self):
        """Test that opposite relationship is symmetric."""
        for anchor in Anchor:
            opposite = anchor.__neg__
            if anchor is not Anchor.CENTER:
                assert opposite.__neg__ is anchor
