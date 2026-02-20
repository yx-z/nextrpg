"""
Tests for nextrpg.core.time module.

Testing Timer and Countdown classes without using pygame.time.get_ticks().
"""

from unittest.mock import patch

import pytest

from nextrpg.core.time import Countdown, Millisecond, Timer


class TestTimer:
    """Tests for Timer class."""

    def test_timer_creation(self):
        """Test creating a Timer."""
        timer = Timer(duration=1000)
        assert timer.duration == 1000
        assert timer.elapsed == 0

    def test_timer_with_elapsed(self):
        """Test creating Timer with elapsed time."""
        timer = Timer(duration=1000, elapsed=500)
        assert timer.duration == 1000
        assert timer.elapsed == 500

    def test_timer_tick(self):
        """Test ticking the timer."""
        timer = Timer(duration=1000)
        new_timer = timer.tick(100)

        # Original should be unchanged
        assert timer.elapsed == 0
        # New timer should have advanced
        assert new_timer.elapsed == 100

    def test_timer_multiple_ticks(self):
        """Test multiple ticks."""
        timer = Timer(duration=1000)
        timer = timer.tick(100)
        timer = timer.tick(200)
        timer = timer.tick(150)

        assert timer.elapsed == 450

    def test_timer_is_complete_false(self):
        """Test is_complete returns False when not done."""
        timer = Timer(duration=1000, elapsed=500)
        assert not timer.is_complete

    def test_timer_is_complete_exact(self):
        """Test is_complete returns True at exact duration."""
        timer = Timer(duration=1000, elapsed=1000)
        assert timer.is_complete

    def test_timer_is_complete_exceeded(self):
        """Test is_complete returns True when exceeded."""
        timer = Timer(duration=1000, elapsed=1100)
        assert timer.is_complete

    def test_timer_completed_percentage(self):
        """Test completed_percentage calculation."""
        timer = Timer(duration=1000, elapsed=500)
        assert timer.completed_percentage == 0.5

    def test_timer_completed_percentage_start(self):
        """Test completed_percentage at start."""
        timer = Timer(duration=1000)
        assert timer.completed_percentage == 0.0

    def test_timer_completed_percentage_end(self):
        """Test completed_percentage at end."""
        timer = Timer(duration=1000, elapsed=1000)
        assert timer.completed_percentage == 1.0

    def test_timer_remaining(self):
        """Test remaining time calculation."""
        timer = Timer(duration=1000, elapsed=300)
        assert timer.remaining == 700

    def test_timer_remaining_at_start(self):
        """Test remaining at start."""
        timer = Timer(duration=1000)
        assert timer.remaining == 1000

    def test_timer_remaining_at_end(self):
        """Test remaining at end."""
        timer = Timer(duration=1000, elapsed=1000)
        assert timer.remaining == 0

    def test_timer_remaining_exceeded(self):
        """Test remaining when exceeded (can be negative)."""
        timer = Timer(duration=1000, elapsed=1100)
        assert timer.remaining == -100

    def test_timer_remaining_percentage(self):
        """Test remaining_percentage calculation."""
        timer = Timer(duration=1000, elapsed=300)
        assert timer.remaining_percentage == 0.7

    def test_timer_reset(self):
        """Test reset property."""
        timer = Timer(duration=1000, elapsed=500)
        reset_timer = timer.reset

        assert reset_timer.elapsed == 0
        assert reset_timer.duration == 1000

    def test_timer_modulo(self):
        """Test modulo property (cycling timer)."""
        timer = Timer(duration=1000, elapsed=1500)
        modulo_timer = timer.modulo

        # Should cycle: 1500 % 1000 = 500
        assert modulo_timer.elapsed == 500
        assert modulo_timer.duration == 1000

    def test_timer_frozen(self):
        """Test that Timer is frozen."""
        timer = Timer(duration=1000)

        with pytest.raises(Exception):  # FrozenInstanceError
            timer.elapsed = 500

    def test_timer_countdown_property(self):
        """Test countdown property returns Countdown."""
        timer = Timer(duration=1000, elapsed=500)
        countdown = timer.countdown

        assert isinstance(countdown, Countdown)
        assert countdown.duration == 1000


class TestCountdown:
    """Tests for Countdown class."""

    def test_countdown_creation(self):
        """Test creating a Countdown."""
        countdown = Countdown(duration=1000)
        # Countdown should start at full duration
        assert countdown.duration == 1000
        assert countdown.elapsed == 1000

    def test_countdown_with_elapsed(self):
        """Test Countdown with different elapsed values."""
        countdown = Countdown(duration=1000, elapsed=500)
        assert countdown.duration == 1000
        assert countdown.elapsed == 500

    def test_countdown_tick(self):
        """Test countdown ticking (counting down)."""
        countdown = Countdown(duration=1000)
        new_countdown = countdown.tick(100)

        # Should count down: 1000 - 100 = 900
        assert new_countdown.elapsed == 900

    def test_countdown_multiple_ticks(self):
        """Test multiple countdown ticks."""
        countdown = Countdown(duration=1000)
        countdown = countdown.tick(100)
        countdown = countdown.tick(200)
        countdown = countdown.tick(150)

        # Should be: 1000 - 100 - 200 - 150 = 550
        assert countdown.elapsed == 550

    def test_countdown_tick_below_zero(self):
        """Test countdown doesn't go below zero."""
        countdown = Countdown(duration=1000, elapsed=100)
        new_countdown = countdown.tick(500)

        # Should be clamped to 0
        assert new_countdown.elapsed == 0

    def test_countdown_is_complete_false(self):
        """Test is_complete returns False when time remains."""
        countdown = Countdown(duration=1000, elapsed=500)
        assert not countdown.is_complete

    def test_countdown_is_complete_true(self):
        """Test is_complete returns True when countdown reaches zero."""
        countdown = Countdown(duration=1000, elapsed=0)
        assert countdown.is_complete

    def test_countdown_completed_percentage(self):
        """Test completed_percentage for countdown."""
        countdown = Countdown(duration=1000, elapsed=500)
        # For countdown: (1000 - 500) / 1000 = 0.5 completed
        assert countdown.completed_percentage == 0.5

    def test_countdown_remaining(self):
        """Test remaining returns elapsed for countdown."""
        countdown = Countdown(duration=1000, elapsed=500)
        # For countdown, remaining is just the elapsed value
        assert countdown.remaining == 500

    def test_countdown_remaining_percentage(self):
        """Test remaining_percentage for countdown."""
        countdown = Countdown(duration=1000, elapsed=500)
        # Percentage of time remaining
        assert countdown.remaining_percentage == 0.5

    def test_countdown_reset(self):
        """Test countdown reset."""
        countdown = Countdown(duration=1000, elapsed=500)
        reset_countdown = countdown.reset

        # Reset for countdown should go back to start (duration)
        assert reset_countdown.elapsed == 1000
        assert reset_countdown.duration == 1000

    def test_countdown_countdown_property(self):
        """Test countdown property returns self (countdown is already a countdown)."""
        countdown = Countdown(duration=1000, elapsed=500)
        # Countdown.countdown should return a new Countdown with same duration
        new_countdown = countdown.countdown

        assert isinstance(new_countdown, Countdown)
        assert new_countdown.duration == 1000


class TestTimerIntegration:
    """Integration tests for Timer and Countdown together."""

    def test_timer_to_countdown_conversion(self):
        """Test converting Timer to Countdown."""
        timer = Timer(duration=1000, elapsed=300)
        countdown = timer.countdown

        assert isinstance(countdown, Countdown)
        assert countdown.duration == 1000
        assert countdown.elapsed == 1000  # Countdown starts fresh

    def test_countdown_timing_sequence(self):
        """Test a realistic countdown sequence."""
        countdown = Countdown(duration=1000)

        # Simulate a countdown from 1000ms to 0
        for i in range(10):
            assert not countdown.is_complete
            countdown = countdown.tick(100)
            assert countdown.elapsed == 1000 - ((i + 1) * 100)

        # Now should be complete
        assert countdown.is_complete

    def test_timer_timing_sequence(self):
        """Test a realistic timer sequence."""
        timer = Timer(duration=1000)

        # Simulate a timer counting from 0 to 1000ms
        for i in range(10):
            assert not timer.is_complete
            timer = timer.tick(100)
            assert timer.elapsed == (i + 1) * 100

        # Now should be complete
        assert timer.is_complete


class TestMillisecondType:
    """Tests for Millisecond type."""

    def test_millisecond_is_int(self):
        """Test that Millisecond type is int."""
        ms: Millisecond = 1000
        assert isinstance(ms, int)
        assert ms == 1000
