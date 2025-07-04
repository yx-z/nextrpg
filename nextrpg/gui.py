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

from nextrpg.config import (
    GuiConfig,
    GuiMode,
    ResizeMode,
    config,
    initial_config,
    set_config,
)
from nextrpg.core import Millisecond, Pixel, Size
from nextrpg.draw_on_screen import Coordinate, DrawOnScreen, Drawing
from nextrpg.event.pygame_event import (
    GuiResize,
    KeyPressDown,
    KeyboardKey,
    PygameEvent,
)
from nextrpg.logger import ComponentAndMessage, Logger, pop_messages
from nextrpg.text import Text

type _GuiFlag = int

logger = Logger("GUI")


def gui_size() -> Size:
    """
    Get the logical size of the GUI window.
    Upon ResizeMode.SCALE, the logical GUI window size shall be the initial
    GUI size given all the scaling logic of game content is handled already
    at `Gui` class internally.

    So any in-game logic of GUI size shall assume the initial GUI size.

    Returns:
        `Size`: The size of the GUI window.
    """
    match config().gui.resize_mode:
        case ResizeMode.SCALE:
            return initial_config().gui.size
        case ResizeMode.KEEP_NATIVE_SIZE:
            return config().gui.size
    raise ValueError(f"Invalid resize mode {config().gui.resize_mode}")


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

        Arguments:
            `e`: The event to process.

        Returns:
            `Gui`: An updated `Gui` instance.
        """
        return self

    def draw(
        self, draw_on_screens: list[DrawOnScreen], time_delta: Millisecond
    ) -> None:
        """
        Draw the given drawings to the screen.

        Arguments:
            `draw_on_screens`: The drawings to draw to the screen.

            `time_delta`: The time that has passed since the last update.

        Returns:
            `None`.
        """
        logger.debug(
            t"Size {self.current_config.size} Shift {self._center_shift}"
        )
        self._screen.fill(self.current_config.background_color)
        match self.current_config.resize_mode:
            case ResizeMode.SCALE:
                self._screen.blit(*self._scale(draw_on_screens).pygame)
            case ResizeMode.KEEP_NATIVE_SIZE:
                self._screen.blits(d.pygame for d in draw_on_screens)
        self._draw_log(time_delta)
        flip()

    def _draw_log(self, time_delta: Millisecond) -> None:
        if msgs := pop_messages(time_delta):
            self._screen.blits(t.draw_on_screen.pygame for t in _log_text(msgs))

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
    current_config = replace(
        self.current_config, gui_mode=self.current_config.gui_mode.opposite
    )
    set_config(replace(config(), gui=current_config))
    return replace(
        self, current_config=current_config, last_config=self.current_config
    )


@Gui.event.register
def _resize(self, e: GuiResize) -> Gui:
    if e.size == self.current_config.size:
        return self
    current_config = replace(self.current_config, size=e.size)
    set_config(replace(config(), gui=current_config))
    return replace(
        self, current_config=current_config, last_config=self.current_config
    )


def _log_text(msgs: list[ComponentAndMessage]) -> list[Text]:
    margin = config().text.margin
    msg_margin = (
        max(config().text.font.text_size(m.component).width for m in msgs)
        + 2 * margin
    )
    return [
        text
        for i, (component, msg) in enumerate(msgs)
        for text in (
            Text(component, Coordinate(margin, _line_height(i))),
            Text(msg, Coordinate(msg_margin, _line_height(i))),
        )
    ]


def _line_height(line_index: int) -> Pixel:
    return 2 * config().text.margin + line_index * config().text.font.size
