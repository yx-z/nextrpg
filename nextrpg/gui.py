"""
Game window / Graphical User Interface (GUI).
"""

from dataclasses import dataclass, field, replace
from functools import cached_property, reduce, singledispatchmethod
from operator import or_

from pygame import font
from pygame.display import flip, init, set_caption, set_mode
from pygame.locals import FULLSCREEN, RESIZABLE
from pygame.surface import Surface
from pygame.transform import scale

from nextrpg.config import GuiConfig, GuiMode, ResizeMode, config, set_config
from nextrpg.draw_on_screen import Coordinate, DrawOnScreen, Drawing
from nextrpg.event.pygame_event import (
    GuiResize,
    KeyPressDown,
    KeyboardKey,
    PygameEvent,
)
from nextrpg.logger import clear_debug_logs, debug_log, get_debug_logs
from nextrpg.text import Text

type _GuiFlag = int


@dataclass
class Gui:
    """
    Initialize a `Gui` instance that scales and centers drawings.
    """

    current_config: GuiConfig = field(default_factory=lambda: config().gui)
    last_config: GuiConfig = field(default_factory=lambda: config().gui)
    initial_config: GuiConfig = field(default_factory=lambda: config().gui)
    _screen: Surface | None = None

    def __post_init__(self) -> None:
        if not self._screen:
            init()
            font.init()
        if self.last_config.title != self.current_config.title:
            set_caption(self.current_config.title)
        if (
            self._screen is None
            or self.last_config.size != self.current_config.size
            or self.last_config.gui_mode != self.current_config.gui_mode
            or self.last_config.allow_window_resize
            != self.current_config.allow_window_resize
        ):
            self._screen = set_mode(
                self.current_config.size, self._current_gui_flag
            )

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
        debug_log("GUI", t"size {self.current_config.size} shift {self._center_shift}")
        self._screen.fill(self.current_config.background_color)
        match self.current_config.resize_mode:
            case ResizeMode.SCALE:
                self._screen.blit(*self._scale(draw_on_screens).pygame)
            case ResizeMode.KEEP_NATIVE_SIZE:
                self._screen.blits(d.pygame for d in draw_on_screens)
        self._draw_debug_log()
        flip()

    def _draw_debug_log(self) -> None:
        if config().debug:
            self._screen.blits(
                d.pygame
                for d in Text(
                     get_debug_logs().formatted_log, Coordinate(0, 0)
                ).draw_on_screens
            )
        clear_debug_logs()

    def _scale(self, draws: list[DrawOnScreen]) -> DrawOnScreen:
        screen = Surface(self.initial_config.size)
        screen.blits(d.pygame for d in draws)
        return DrawOnScreen(
            self._center_shift,
            Drawing(
                scale(screen, self.initial_config.size.scale(self._scaling))
            ),
        )

    @cached_property
    def _scaling(self) -> float:
        current_width, current_height = self.current_config.size
        initial_width, initial_height = self.initial_config.size
        return min(
            current_width / initial_width, current_height / initial_height
        )

    @cached_property
    def _center_shift(self) -> Coordinate:
        current_width, current_height = self.current_config.size
        initial_width, initial_height = self.initial_config.size
        return Coordinate(
            (current_width - self._scaling * initial_width) / 2,
            (current_height - self._scaling * initial_height) / 2,
        )

    @cached_property
    def _current_gui_flag(self) -> _GuiFlag:
        check_and_flags = [
            (self.current_config.gui_mode is GuiMode.FULL_SCREEN, FULLSCREEN),
            (self.current_config.allow_window_resize, RESIZABLE),
        ]
        return reduce(
            or_, [flag for check, flag in check_and_flags if check], 0
        )


@Gui.event.register
def _toggle_gui_mode(self, e: KeyPressDown) -> Gui:
    if e.key is not KeyboardKey.GUI_MODE_TOGGLE:
        return self
    current_config = self.current_config._replace(
        gui_mode=self.current_config.gui_mode.opposite
    )
    set_config(config()._replace(gui=current_config))
    return replace(
        self, current_config=current_config, last_config=self.current_config
    )


@Gui.event.register
def _resize(self, e: GuiResize) -> Gui:
    if e.size == self.current_config.size:
        return self
    current_config = self.current_config._replace(size=e.size)
    set_config(config()._replace(gui=current_config))
    return replace(
        self, current_config=current_config, last_config=self.current_config
    )
