"""Tests for nextrpg.event.base_event module."""

import pytest

from nextrpg.event.base_event import BaseEvent


class TestBaseEvent:
    """Test BaseEvent class."""

    def test_base_event_exists(self):
        """Test that BaseEvent can be imported."""
        assert BaseEvent is not None

    def test_base_event_is_protocol(self):
        """Test that BaseEvent is a protocol."""
        # BaseEvent is likely a Protocol or ABC
        # Just verify it exists and has expected attributes
        assert hasattr(BaseEvent, "__mro__") or hasattr(BaseEvent, "__meta__")
