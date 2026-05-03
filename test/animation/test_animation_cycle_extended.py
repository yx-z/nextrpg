"""Extended tests for nextrpg.animation.cycle module."""
import pytest
from test.util import MockSprite
from nextrpg.animation.cycle import Cycle
from nextrpg.animation.sequence import Sequence


class TestCycleIsSubclassOfSequence:
    """Tests for Cycle inheritance."""

    def test_cycle_is_subclass_of_sequence(self):
        """Test that Cycle is a subclass of Sequence."""
        assert issubclass(Cycle, Sequence)

    def test_cycle_creation_with_multiple_sprites(self):
        """Test creating a Cycle with multiple sprites."""
        sprites = (MockSprite(), MockSprite(), MockSprite())
        cycle = Cycle(sprites)
        assert cycle.resource == sprites
        assert len(cycle.resources) == 3


class TestCycleCreation:
    """Tests for Cycle creation."""

    def test_cycle_with_tuple_of_sprites(self):
        """Test creating a Cycle with a tuple of sprites."""
        sprites = (MockSprite(), MockSprite())
        cycle = Cycle(sprites)
        assert cycle is not None
        assert len(cycle.resources) == 2

    def test_cycle_copy_is_tuple(self):
        """Test Cycle._copy is a tuple of shifted sprites."""
        sprites = (MockSprite(), MockSprite())
        cycle = Cycle(sprites)
        assert isinstance(cycle._copy, tuple)
        assert len(cycle._copy) == 2

    def test_cycle_copy_matches_resources(self):
        """Test Cycle._copy matches resources on creation."""
        sprites = (MockSprite(), MockSprite(), MockSprite())
        cycle = Cycle(sprites)
        assert len(cycle._copy) == len(cycle.resources)


class TestCycleNeverCompletes:
    """Tests that Cycle never reports completion."""

    def test_cycle_is_not_complete_initially(self):
        """Test Cycle is not complete initially."""
        sprites = (MockSprite(), MockSprite())
        cycle = Cycle(sprites)
        assert cycle.is_complete is False
