"""
Game window / Graphical User Interface (GUI).
"""

from dataclasses import KW_ONLY, dataclass, field, replace
from functools import cached_property

from pygame import FULLSCREEN, RESIZABLE, Surface
from pygame.display import flip, get_window_size, init, set_caption, set_mode
from pygame.transform import smoothscale

from nextrpg.config import GuiMode, ResizeMode, config
from nextrpg.core import (
    Coordinate,
    INTERNAL,
    Size,
    initialize_internal_field,
    is_internal_field_initialized,
)
from nextrpg.draw_on_screen import DrawOnScreen, Drawing
from nextrpg.event.pygame_event import GuiResize


@dataclass(frozen=True)
class Gui:
    """
    Initialize a `Gui` instance that scales and centers drawings.

    Args:
        `window`: Size of the window. If `None`, default to
            the GUI size from `config().gui`.
    """

    window: Size = field(default_factory=lambda: config().gui.size)
    _: KW_ONLY = INTERNAL
    _screen: Surface = INTERNAL

    @staticmethod
    def current_size() -> Size:
        """
        Get the current size of the window.

        Returns:
            `Size`: The current size of the window.
        """
        return Size(*get_window_size())

    def resize(self, event: GuiResize) -> "Gui":
        """
        Resize the window to the given size.

        Args:
            `event`: The event containing the new window size.

        Returns:
            `Gui`: A new `Gui` instance with the updated window size.
        """
        return replace(self, window=event.size)

    def draw(self, draw_on_screens: list[DrawOnScreen]) -> None:
        self._screen.fill(config().gui.background_color.tuple)
        match config().gui.resize_mode:
            case ResizeMode.SCALE:
                self._screen.blit(*self._scale(draw_on_screens).pygame)
            case ResizeMode.KEEP_NATIVE:
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
        return min(
            self.window.width / config().gui.size.width,
            self.window.height / config().gui.size.height,
        )

    @cached_property
    def _center_shift(self) -> Coordinate:
        return Coordinate(
            (self.window.width - self._scaling * config().gui.size.width) / 2,
            (self.window.height - self._scaling * config().gui.size.height) / 2,
        )

    def __post_init__(self) -> None:
        if is_internal_field_initialized(self._screen):
            return
        init()
        set_caption(config().gui.title)
        initialize_internal_field(self, "_screen", _init_screen)


def _init_screen() -> Surface:
    return set_mode(config().gui.size.tuple, _gui_flag())


def _gui_flag() -> int:
    flag = 0
    if config().gui.gui_mode is GuiMode.FULL_SCREEN:
        flag |= FULLSCREEN
    if config().gui.allow_window_resize:
        flag |= RESIZABLE
    return flag
