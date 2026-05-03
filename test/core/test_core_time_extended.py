"""Extended tests for nextrpg.core.time module."""
import pytest
from nextrpg.core.time import Timer, Countdown


class TestTimerCompletedPercentage:
    """Tests for Timer.completed_percentage."""

    def test_completed_percentage_at_start(self):
        """Test completed_percentage is 0 at start."""
        timer = Timer(duration=1000)
        assert timer.completed_percentage == pytest.approx(0.0)

    def test_completed_percentage_at_half(self):
        """Test completed_percentage is 0.5 at halfway."""
        timer = Timer(duration=1000, elapsed=500)
        assert timer.completed_percentage == pytest.approx(0.5)

    def test_completed_percentage_at_end(self):
        """Test completed_percentage is 1.0 at completion."""
        timer = Timer(duration=1000, elapsed=1000)
        assert timer.completed_percentage == pytest.approx(1.0)

    def test_completed_percentage_over_end(self):
        """Test completed_percentage can exceed 1.0 if over-ticked."""
        timer = Timer(duration=1000, elapsed=1500)
        assert timer.completed_percentage == pytest.approx(1.5)


class TestTimerRemainingPercentage:
    """Tests for Timer.remaining_percentage."""

    def test_remaining_percentage_at_start(self):
        """Test remaining_percentage is 1.0 at start."""
        timer = Timer(duration=1000)
        assert timer.remaining_percentage == pytest.approx(1.0)

    def test_remaining_percentage_at_half(self):
        """Test remaining_percentage is 0.5 at halfway."""
        timer = Timer(duration=1000, elapsed=500)
        assert timer.remaining_percentage == pytest.approx(0.5)

    def test_remaining_percentage_at_end(self):
        """Test remaining_percentage is 0.0 at completion."""
        timer = Timer(duration=1000, elapsed=1000)
        assert timer.remaining_percentage == pytest.approx(0.0)


class TestTimerModulo:
    """Tests for Timer.modulo property."""

    def test_modulo_within_duration(self):
        """Test modulo when elapsed is less than duration."""
        timer = Timer(duration=1000, elapsed=300)
        mod = timer.modulo
        assert mod.elapsed == 300

    def test_modulo_at_exact_duration(self):
        """Test modulo when elapsed equals duration."""
        timer = Timer(duration=1000, elapsed=1000)
        mod = timer.modulo
        assert mod.elapsed == 0

    def test_modulo_beyond_duration(self):
        """Test modulo wraps around when elapsed exceeds duration."""
        timer = Timer(duration=1000, elapsed=1300)
        mod = timer.modulo
        assert mod.elapsed == 300

    def test_modulo_twice_duration(self):
        """Test modulo wraps around at exactly twice the duration."""
        timer = Timer(duration=1000, elapsed=2000)
        mod = timer.modulo
        assert mod.elapsed == 0


class TestTimerImmutability:
    """Tests for Timer immutability."""

    def test_timer_tick_returns_new_instance(self):
        """Test tick returns a new Timer instance."""
        timer = Timer(duration=1000)
        ticked = timer.tick(100)
        assert ticked is not timer
        assert ticked.elapsed == 100
        assert timer.elapsed == 0

    def test_timer_reset_returns_new_instance(self):
        """Test reset returns a new Timer instance."""
        timer = Timer(duration=1000, elapsed=500)
        reset = timer.reset
        assert reset is not timer
        assert reset.elapsed == 0


class TestCountdownBehavior:
    """Tests for Countdown-specific behavior."""

    def test_countdown_starts_at_duration(self):
        """Test Countdown starts with elapsed=duration."""
        countdown = Countdown(duration=1000)
        assert countdown.elapsed == 1000

    def test_countdown_tick_decrements(self):
        """Test ticking a Countdown decrements elapsed."""
        countdown = Countdown(duration=1000)
        ticked = countdown.tick(200)
        assert ticked.elapsed == 800

    def test_countdown_clamps_at_zero(self):
        """Test Countdown elapsed is clamped to 0."""
        countdown = Countdown(duration=1000)
        ticked = countdown.tick(2000)
        assert ticked.elapsed == 0

    def test_countdown_complete_when_zero(self):
        """Test Countdown is complete when elapsed is 0."""
        countdown = Countdown(duration=1000)
        ticked = countdown.tick(1000)
        assert ticked.is_complete

    def test_countdown_not_complete_initially(self):
        """Test Countdown is not complete at start."""
        countdown = Countdown(duration=1000)
        assert not countdown.is_complete

    def test_countdown_remaining_percentage_at_start(self):
        """Test Countdown remaining_percentage at start."""
        countdown = Countdown(duration=1000)
        # elapsed=1000, remaining=0, remaining_percentage=0
        assert countdown.remaining_percentage == pytest.approx(0.0)

    def test_countdown_completed_percentage_at_start(self):
        """Test Countdown completed_percentage at start."""
        countdown = Countdown(duration=1000)
        # elapsed=1000, completed_percentage=1.0
        assert countdown.completed_percentage == pytest.approx(1.0)

    def test_countdown_reset_goes_back_to_duration(self):
        """Test Countdown reset restores elapsed to duration."""
        countdown = Countdown(duration=1000)
        ticked = countdown.tick(500)
        assert ticked.elapsed == 500
        reset = ticked.reset
        assert reset.elapsed == 1000
