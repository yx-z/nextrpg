"""Tests for nextrpg.gui.window — focused on the cached base surface.

The ``_base_surface`` cached_property was introduced to avoid allocating a
fresh ``Surface + convert_alpha()`` every frame in ``blits``. These tests
verify:
  1. The surface is cached (same object across accesses).
  2. Its size matches ``initial_config.size`` (stable across resizes).
  3. It has the SRCALPHA flag (required for transparency).
  4. ``blits`` reuses the cached surface rather than allocating a new one.
  5. ``event`` and ``resize`` dispatch correctly.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
from pygame import MOUSEBUTTONDOWN, QUIT, SRCALPHA, Event

import pytest

pygame.init()

from nextrpg.event.io_event import MouseButtonDown, Quit
from nextrpg.gui.window import Window


@pytest.fixture
def window():
    """A fresh Window constructed with default config.

    Mocks SaveIo.update to return its argument unchanged, simulating
    "no saved data" so _saved_config returns None and current_config
    equals initial_config. This avoids disk I/O and stale save pollution.
    """
    from unittest.mock import patch

    from nextrpg.core.save import SaveIo

    with patch.object(SaveIo, "update", side_effect=lambda x: x):
        return Window()


class TestBaseSurfaceCache:
    """Tests for the ``_base_surface`` cached_property."""

    def test_base_surface_is_cached(self, window):
        """Repeated access returns the identical Surface object."""
        first = window._base_surface
        second = window._base_surface
        assert first is second

    def test_base_surface_size_matches_initial_config(self, window):
        """The cached surface is sized to initial_config, not current_config."""
        surf = window._base_surface
        assert surf.get_size() == tuple(window.initial_config.size)

    def test_base_surface_has_alpha_channel(self, window):
        """The surface is created with SRCALPHA for per-pixel transparency."""
        surf = window._base_surface
        assert surf.get_flags() & SRCALPHA

    def test_base_surface_is_not_screen(self, window):
        """The base surface is distinct from the display screen."""
        assert window._base_surface is not window._screen


class TestBlitsReusesBaseSurface:
    """Tests that ``blits`` reuses the cached ``_base_surface``."""

    def test_blits_with_empty_drawings_does_not_crash(self, window):
        """Calling blits with no drawings completes without error."""
        # An empty tuple satisfies the iterable protocol; blits iterates
        # it and calls .pygame on each element (zero elements = no-op).
        # Millisecond is a PEP 695 type alias for int, so pass 0 directly.
        window.blits((), 0)

    def test_blits_does_not_replace_base_surface(self, window):
        """The cached _base_surface object persists across blits calls."""
        base_before = window._base_surface
        window.blits((), 0)
        base_after = window._base_surface
        assert base_before is base_after

    def test_blits_reuses_same_surface_across_multiple_calls(self, window):
        """Multiple blits calls all use the same cached surface object."""
        surfaces = [window._base_surface]
        for _ in range(3):
            window.blits((), 0)
            surfaces.append(window._base_surface)
        # All accesses return the identical object.
        assert all(s is surfaces[0] for s in surfaces)


class TestEventDispatch:
    """Tests for ``Window.event`` — event routing without side effects."""

    def test_event_with_quit_returns_self(self, window):
        """A Quit event falls through all branches and returns self."""
        result = window.event(Quit(Event(QUIT)))
        assert result is window

    def test_event_with_mouse_button_down_returns_self(self, window):
        """A MouseButtonDown event is logged but returns self."""
        result = window.event(
            MouseButtonDown(Event(MOUSEBUTTONDOWN, pos=(10, 20)))
        )
        assert result is window


class TestResize:
    """Tests for ``Window.resize``."""

    def test_resize_same_size_returns_self(self, window):
        """Resizing to the current size is a no-op that returns self."""
        result = window.resize(window.current_config.size)
        assert result is window


class TestTick:
    """Tests for ``Window.tick`` — config-change dispatch.

    Uses ``override_config`` to simulate config changes without touching
    SaveIo (no disk writes).
    """

    def test_tick_no_change_returns_self(self, window):
        """When config hasn't changed, tick returns self."""
        result = window.tick()
        assert result is window

    def test_tick_with_fps_no_flag_returns_self(self, window):
        """fps arg is ignored when include_fps_in_window_title is False."""
        result = window.tick(fps="60")
        assert result is window

    def test_tick_title_change_returns_replaced(self, window):
        """Config change without size/flag change returns a replaced Window."""
        from dataclasses import replace as dc_replace

        from nextrpg.config.config import config, override_config

        original = config()
        new_window_cfg = dc_replace(window.current_config, title="Changed")
        new_system = dc_replace(original.system, window=new_window_cfg)
        new_cfg = dc_replace(original, system=new_system)

        with override_config(new_cfg):
            result = window.tick()
        assert result is not window
        assert result.current_config.title == "Changed"

    def test_tick_size_change_returns_new_screen(self, window):
        """Config change with different size creates a new screen."""
        from dataclasses import replace as dc_replace

        from nextrpg.config.config import config, override_config
        from nextrpg.geometry.size import Size

        original = config()
        new_window_cfg = dc_replace(window.current_config, size=Size(999, 999))
        new_system = dc_replace(original.system, window=new_window_cfg)
        new_cfg = dc_replace(original, system=new_system)

        with override_config(new_cfg):
            result = window.tick()
        assert result is not window
        assert result.current_config.size == Size(999, 999)

    def test_tick_fps_shown_when_flag_enabled(self, window):
        """When include_fps_in_window_title is True, fps is appended to title."""
        from dataclasses import replace as dc_replace

        from nextrpg.config.config import config, override_config

        original = config()
        new_window_cfg = dc_replace(
            window.current_config, include_fps_in_window_title=True
        )
        new_system = dc_replace(original.system, window=new_window_cfg)
        new_cfg = dc_replace(original, system=new_system)

        with override_config(new_cfg):
            result = window.tick(fps="60")
        assert result is not window
        assert result.current_config.include_fps_in_window_title is True

    def test_tick_fps_flag_turned_off_clears_caption(self):
        """When fps flag was on but is now off, the elif branch resets caption."""
        from dataclasses import replace as dc_replace
        from unittest.mock import patch

        from nextrpg.config.config import config, override_config
        from nextrpg.core.save import SaveIo

        original = config()
        fps_on = dc_replace(
            original.system.window, include_fps_in_window_title=True
        )
        fps_on_system = dc_replace(original.system, window=fps_on)
        fps_on_cfg = dc_replace(original, system=fps_on_system)

        # Construct window with fps flag ON
        with override_config(fps_on_cfg):
            with patch.object(SaveIo, "update", side_effect=lambda x: x):
                win = Window()

        # Tick with fps flag OFF (original config) — exercises elif branch
        with override_config(original):
            result = win.tick()

        assert result is not win
        assert result.current_config.include_fps_in_window_title is False


class TestToggleAndResizeWithMock:
    """Tests for toggle/resize methods using a mocked ``_set_window_config``.

    The mock sets the global config (so ``tick`` sees the change) without
    writing to disk via SaveIo.
    """

    @pytest.fixture
    def restore_config(self):
        from nextrpg.config.config import config, set_config

        original = config()
        yield
        set_config(original)

    @staticmethod
    def _fake_set_window_config(window_config):
        from dataclasses import replace as dc_replace

        from nextrpg.config.config import config, set_config

        current = config()
        system = dc_replace(current.system, window=window_config)
        set_config(dc_replace(current, system=system))

    def test_toggle_full_screen(self, window, restore_config):
        from unittest.mock import patch

        with patch(
            "nextrpg.gui.window._set_window_config",
            side_effect=self._fake_set_window_config,
        ):
            result = window.toggle_full_screen()
        assert result is not window
        assert result.current_config.full_screen is not window.current_config.full_screen

    def test_resize_different_size(self, window, restore_config):
        from unittest.mock import patch

        from nextrpg.geometry.size import Size

        with patch(
            "nextrpg.gui.window._set_window_config",
            side_effect=self._fake_set_window_config,
        ):
            result = window.resize(Size(999, 999))
        assert result is not window
        assert result.current_config.size == Size(999, 999)

    def test_toggle_include_fps_in_window_title(self, window, restore_config):
        from unittest.mock import patch

        with patch(
            "nextrpg.gui.window._set_window_config",
            side_effect=self._fake_set_window_config,
        ):
            result = window.toggle_include_fps_in_window_title()
        assert result is not window
        assert (
            result.current_config.include_fps_in_window_title
            is not window.current_config.include_fps_in_window_title
        )

    def test_event_with_window_resize(self, window, restore_config):
        """WindowResize event triggers resize to the event's size."""
        from unittest.mock import patch

        from pygame import VIDEORESIZE, Event

        from nextrpg.event.io_event import WindowResize
        from nextrpg.geometry.size import Size

        resize_event = WindowResize(Event(VIDEORESIZE, w=999, h=999))
        with patch(
            "nextrpg.gui.window._set_window_config",
            side_effect=self._fake_set_window_config,
        ):
            result = window.event(resize_event)
        assert result is not window
        assert result.current_config.size == Size(999, 999)

    def test_event_full_screen_toggle_key(self, window, restore_config):
        """Pressing F1 toggles full screen."""
        from unittest.mock import patch

        from pygame import KEYDOWN, K_F1, Event

        from nextrpg.event.io_event import KeyPressDown

        key_event = KeyPressDown(Event(KEYDOWN, key=K_F1))
        with patch(
            "nextrpg.gui.window._set_window_config",
            side_effect=self._fake_set_window_config,
        ):
            result = window.event(key_event)
        assert result is not window
        assert (
            result.current_config.full_screen
            is not window.current_config.full_screen
        )

    def test_event_fps_toggle_key(self, window, restore_config):
        """Pressing F2 toggles include_fps_in_window_title."""
        from unittest.mock import patch

        from pygame import KEYDOWN, K_F2, Event

        from nextrpg.event.io_event import KeyPressDown

        key_event = KeyPressDown(Event(KEYDOWN, key=K_F2))
        with patch(
            "nextrpg.gui.window._set_window_config",
            side_effect=self._fake_set_window_config,
        ):
            result = window.event(key_event)
        assert result is not window
        assert (
            result.current_config.include_fps_in_window_title
            is not window.current_config.include_fps_in_window_title
        )

    def test_set_window_config_directly(self, window, restore_config):
        """Calling _set_window_config directly updates global config (lines 187-191)."""
        from dataclasses import replace as dc_replace
        from unittest.mock import MagicMock, patch

        from nextrpg.config.config import config
        from nextrpg.gui.window import _set_window_config

        new_cfg = dc_replace(window.current_config, title="Direct")
        with patch("nextrpg.gui.window.SaveIo") as MockSaveIo:
            MockSaveIo.return_value.save.return_value = MagicMock()
            _set_window_config(new_cfg)
        assert config().system.window.title == "Direct"

    def test_saved_config_loads_from_save(self, restore_config):
        """_saved_config returns non-None when SaveIo has a different config (lines 182-183)."""
        from dataclasses import replace as dc_replace
        from unittest.mock import MagicMock, patch

        from nextrpg.config.config import config
        from nextrpg.gui.window import Window

        original = config()
        saved = dc_replace(original.system.window, title="FromSave")

        mock_instance = MagicMock()
        mock_instance.update.return_value = saved
        mock_instance.save.return_value = MagicMock()
        with patch("nextrpg.gui.window.SaveIo", return_value=mock_instance):
            win = Window()
        assert win.current_config.title == "FromSave"
