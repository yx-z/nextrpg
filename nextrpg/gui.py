"""
Game window / Graphical User Interface (GUI).
"""

from __future__ import annotations

from dataclasses import KW_ONLY, field, replace
from functools import cached_property, reduce, singledispatchmethod
from operator import or_

from pygame import FULLSCREEN, RESIZABLE, Surface
from pygame.display import flip, get_window_size, init, set_caption, set_mode
from pygame.transform import smoothscale

from nextrpg.config import GuiMode, ResizeMode, config
from nextrpg.core import Size
from nextrpg.draw_on_screen import Coordinate, DrawOnScreen, Drawing
from nextrpg.event.pygame_event import (
    GuiResize,
    KeyPressDown,
    KeyboardKey,
    PygameEvent,
)
from nextrpg.model import Model, internal_field


def _init_screen(self: Gui) -> Surface:
    init()
    set_caption(config().gui.title)
    return set_mode(config().gui.size.tuple, _gui_flag(self._gui_mode))


class Gui(Model):
    """
    Initialize a `Gui` instance that scales and centers drawings.

    Args:
        `window`: Size of the window. If `None`, default to
            the GUI size from `config().gui`.
    """

    window: Size = field(default_factory=lambda: config().gui.size)
    _: KW_ONLY = field()
    _gui_mode: GuiMode = internal_field(lambda _: config().gui.gui_mode)
    _screen: Surface = internal_field(_init_screen)

    @staticmethod
    def current_size() -> Size:
        """
        Get the current size of the window.
        This shall be consistent with the `window` property.
        However, this provides global access to the window size without
        retrieving a `Gui` instance.

        Returns:
            `Size`: The current size of the window.
        """
        return Size(*get_window_size())

    @singledispatchmethod
    def event(self, e: PygameEvent) -> Gui:
        """
        `Gui` will action on `KeyPressDown` and `GuiResize` events.
            `KeyPressDown` will toggle between windowed and fullscreen GUI mode,
                upon `KeyboardKey.GUI_MODE_TOGGLE`.

            `GuiResize` will scale the screen appropriately based on config.

        Args:
            `e`: The event to process.

        Returns:
            `Gui`: An updated `Gui` instance.
        """
        return self

    def draw(self, draw_on_screens: list[DrawOnScreen]) -> None:
        """
        Draw the given drawings to the screen.

        Args:
            `draw_on_screens`: The drawings to draw to the screen.

        Returns:
            `None`.
        """
        self._screen.fill(config().gui.background_color.tuple)
        match config().gui.resize_mode:
            case ResizeMode.SCALE:
                self._screen.blit(*self._scale(draw_on_screens).pygame)
            case ResizeMode.KEEP_NATIVE_SIZE:
                self._screen.blits(d.pygame for d in draw_on_screens)
        flip()

    def _scale(self, draws: list[DrawOnScreen]) -> DrawOnScreen:
        screen = Surface(config().gui.size.tuple)
        screen.blits(d.pygame for d in draws)
        scaled_size = config().gui.size * self._scaling
        return DrawOnScreen(
            self._center_shift, Drawing(smoothscale(screen, scaled_size.tuple))
        )

    @cached_property
    def _scaling(self) -> float:
        current_width, current_height = self.window.tuple
        native_width, native_height = config().gui.size.tuple
        return min(current_width / native_width, current_height / native_height)

    @cached_property
    def _center_shift(self) -> Coordinate:
        current_width, current_height = self.window.tuple
        native_width, native_height = config().gui.size.tuple
        return Coordinate(
            (current_width - self._scaling * native_width) / 2,
            (current_height - self._scaling * native_height) / 2,
        )


type _GuiFlag = int


def _gui_flag(gui_mode: GuiMode) -> _GuiFlag:
    check_and_flags = [
        (gui_mode is GuiMode.FULL_SCREEN, FULLSCREEN),
        (config().gui.allow_window_resize, RESIZABLE),
    ]
    flags = [flag for check, flag in check_and_flags if check]
    return reduce(or_, flags, 0)


@Gui.event.register
def _toggle_gui_mode(self, e: KeyPressDown) -> Gui:
    is_toggle_key = e.key is KeyboardKey.GUI_MODE_TOGGLE
    allow_toggle = config().gui.allow_gui_mode_toggle
    if is_toggle_key and allow_toggle:
        updated_mode = self._gui_mode.opposite
        return replace(
            self,
            _gui_mode=updated_mode,
            _screen=set_mode(self.window.tuple, _gui_flag(updated_mode)),
        )
    return self


@Gui.event.register
def _resize(self, e: GuiResize) -> Gui:
    return replace(self, window=e.size)
