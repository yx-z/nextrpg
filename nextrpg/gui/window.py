"""
Game window / Graphical User Interface (GUI).
"""

from dataclasses import dataclass, field, replace
from functools import cached_property

from pygame import DOUBLEBUF, font
from pygame.display import flip, init, set_caption, set_mode
from pygame.locals import FULLSCREEN, RESIZABLE
from pygame.surface import Surface
from pygame.transform import smoothscale

from nextrpg.config import (
    GuiConfig,
    GuiMode,
    ResizeMode,
    config,
    set_config,
)
from nextrpg.core import Millisecond, Pixel, Size
from nextrpg.draw.draw_on_screen import DrawOnScreen, Drawing
from nextrpg.draw.coordinate import Coordinate
from nextrpg.draw.text import Text
from nextrpg.event.pygame_event import (
    GuiResize,
    KeyPressDown,
    KeyboardKey,
    PygameEvent,
)
from nextrpg.logger import ComponentAndMessage, Logger, pop_messages
from nextrpg.draw.text_on_screen import TextOnScreen

type _GuiFlag = int

logger = Logger("GUI")


@dataclass(frozen=True)
class Gui:
    """
    Initialize a `Gui` instance that scales and centers drawings.
    """

    current_config: GuiConfig = field(default_factory=lambda: config().gui)
    last_config: GuiConfig = field(default_factory=lambda: config().gui)
    initial_config: GuiConfig = field(default_factory=lambda: config().gui)
    _screen: Surface | None = None
    _title: str | None = None

    def __post_init__(self) -> None:
        if not self._screen:
            init()
            font.init()

        self._update_title()
        self._update_screen()

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
        match e:
            case GuiResize():
                return self._resize(e.size)
            case KeyPressDown():
                if e.key is KeyboardKey.GUI_MODE_TOGGLE:
                    return self._toggle_gui_mode
        return self

    def draw(
        self, draw_on_screens: tuple[DrawOnScreen, ...], time_delta: Millisecond
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
            t"Size {self.current_config.size} Shift {self._center_shift}",
            duration=None,
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
            self._screen.blits(
                d.pygame for t in _log_text(msgs) for d in t.draw_on_screen
            )

    def _scale(self, draws: tuple[DrawOnScreen, ...]) -> DrawOnScreen:
        screen = Surface(self.initial_config.size)
        screen.blits(d.pygame for d in draws)
        return DrawOnScreen(
            self._center_shift,
            Drawing(
                smoothscale(
                    screen, self.initial_config.size.scale(self._scaling)
                )
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
        flag = DOUBLEBUF
        if self.current_config.gui_mode is GuiMode.FULL_SCREEN:
            flag |= FULLSCREEN
        if self.current_config.allow_window_resize:
            flag |= RESIZABLE
        return flag

    def _update_title(self) -> None:
        if (
            self._title is None
            or self.current_config.title != self.last_config.title
        ):
            object.__setattr__(self, "_title", self.current_config.title)
            set_caption(self._title)

    def _update_screen(self) -> None:
        if (
            self._screen is None
            or self.last_config.size != self.current_config.size
            or self.last_config.gui_mode != self.current_config.gui_mode
            or self.last_config.allow_window_resize
            != self.current_config.allow_window_resize
        ):
            object.__setattr__(
                self,
                "_screen",
                set_mode(self.current_config.size, self._current_gui_flag),
            )

    @cached_property
    def _toggle_gui_mode(self) -> Gui:
        current_config = replace(
            self.current_config, gui_mode=self.current_config.gui_mode.opposite
        )
        set_config(replace(config(), gui=current_config))
        return replace(
            self, current_config=current_config, last_config=self.current_config
        )

    def _resize(self, size: Size) -> Gui:
        if size == self.current_config.size:
            return self
        current_config = replace(self.current_config, size=size)
        set_config(replace(config(), gui=current_config))
        return replace(
            self, current_config=current_config, last_config=self.current_config
        )


def _log_text(
    msgs: tuple[ComponentAndMessage, ...],
) -> tuple[TextOnScreen, ...]:
    spacing = config().text.line_spacing
    msg_spacing = (
        max(config().text.font.text_size(m.component).width for m in msgs)
        + 2 * spacing
    )
    return tuple(
        text
        for i, (component, msg) in enumerate(msgs)
        for text in (
            TextOnScreen(Text(component), Coordinate(spacing, _line_height(i))),
            TextOnScreen(Text(msg), Coordinate(msg_spacing, _line_height(i))),
        )
    )


def _line_height(line_index: int) -> Pixel:
    return config().text.line_spacing + line_index * (
        config().text.line_spacing + config().text.font.text_height
    )
