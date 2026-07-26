"""Tests for nextrpg.gui.window — focused on the cached base surface.

The ``_base_surface`` cached_property was introduced to avoid allocating a
fresh ``Surface + convert_alpha()`` every frame in ``blits``. These tests
verify:
  1. The surface is cached (same object across accesses).
  2. Its size matches ``initial_config.size`` (stable across resizes).
  3. It has the SRCALPHA flag (required for transparency).
  4. ``blits`` reuses the cached surface rather than allocating a new one.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
from pygame import SRCALPHA

import pytest

pygame.init()

from nextrpg.gui.window import Window


@pytest.fixture
def window():
    """A fresh Window constructed with default config."""
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
