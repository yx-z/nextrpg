"""Tests for nextrpg.event.background_event module."""

from unittest.mock import MagicMock, patch

import pytest

from nextrpg.event.background_event import BackgroundEvent


@pytest.mark.skip(
    reason="BackgroundEvent is abstract - cannot instantiate directly"
)
class TestAllBackgroundEvents:
    """BackgroundEvent is abstract and cannot be tested directly."""

    def test_placeholder(self):
        """Placeholder test."""
        pass
