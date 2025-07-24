"""
Game window and Graphical User Interface (GUI) management for `nextrpg`.

This module provides the core GUI system for `nextrpg` games, handling window
management, screen rendering, and user interface interactions. It includes the
`Gui` class which manages the game window, screen scaling, and drawing
operations.

Features:
    - Window management with fullscreen and windowed modes
    - Automatic screen scaling and centering
    - Event handling for window resizing and mode switching
    - Drawing surface management and rendering
    - Integration with the logging system for debug output
"""

from dataclasses import KW_ONLY, dataclass, field, replace
from functools import cached_property
from typing import Self

from pygame import DOUBLEBUF, font
from pygame.display import flip, init, set_caption, set_mode
from pygame.locals import FULLSCREEN, RESIZABLE
from pygame.surface import Surface
from pygame.transform import smoothscale

from nextrpg import Drawing
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dataclass_with_instance_init import not_constructor_below
from nextrpg.core.dimension import Pixel, Size
from nextrpg.core.logger import ComponentAndMessage, Logger, pop_messages
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw_on_screen import DrawOnScreen
from nextrpg.draw.text import Text
from nextrpg.draw.text_on_screen import TextOnScreen
from nextrpg.event.pygame_event import (
    GuiResize,
    KeyboardKey,
    KeyPressDown,
    PygameEvent,
)
from nextrpg.global_config.global_config import config, set_config
from nextrpg.global_config.gui_config import GuiConfig, GuiMode, ResizeMode

logger = Logger("GUI")


@dataclass(frozen=True)
class Window:
    """
    Game window and GUI management system.

    This class handles the game window, screen rendering, and user
    interface interactions. It manages window modes (fullscreen/windowed),
    screen scaling, and drawing operations.

    The GUI system automatically initializes pygame display and font
    systems, manages window configuration, and provides methods for
    drawing and event handling.

    Arguments:
        `current_config`: The current GUI configuration settings.
            Defaults to the global GUI configuration.

        `last_config`: The previous GUI configuration for change detection.
            Defaults to the global GUI configuration.

        `initial_config`: The initial GUI configuration for scaling.
            Defaults to the global GUI configuration.

        `_screen`: Internal pygame surface for the game window.
            Initialized automatically if not provided.

        `_title`: Internal window title cache for optimization.

    Example:
        ```python
        from nextrpg.window import Gui
        from nextrpg.gui_config import GuiConfig, GuiMode

        # Create GUI with custom global_config
        global_config = GuiConfig(size=Size(800, 600), gui_mode=GuiMode.WINDOWED)
        gui = Gui(current_config=global_config)

        # Draw game elements
        gui.draw(drawings, time_delta)
        ```
    """

    _: KW_ONLY = not_constructor_below()
    current_config: GuiConfig = field(default_factory=lambda: config().gui)
    last_config: GuiConfig = field(default_factory=lambda: config().gui)
    initial_config: GuiConfig = field(default_factory=lambda: config().gui)
    _screen: Surface | None = None
    _title: str | None = None

    @property
    def update(self) -> Self:
        """
        Update GUI configuration if needed.

        Checks if the current GUI configuration matches the global global_config
        and updates it if necessary. This ensures GUI settings are
        synchronized with configuration changes.

        Returns:
            `Window`: Updated GUI instance with current configuration.
        """
        if config().gui is self.current_config:
            return self
        return replace(
            self, current_config=config().gui, last_config=self.current_config
        )

    def event(self, e: PygameEvent) -> Self:
        """
        Handle GUI-related events.

        Processes events that affect the GUI system, including:
        - `GuiResize`: Handles window resize events and updates scaling
        - `KeyPressDown`: Toggles between windowed and fullscreen modes
            when `KeyboardKey.GUI_MODE_TOGGLE` is pressed

        Arguments:
            `e`: The pygame event to process.

        Returns:
            `Window`: An updated GUI instance reflecting any changes.

        Example:
            ```python
            from nextrpg.pygame_event import GuiResize, KeyPressDown

            # Handle window resize
            gui = gui.event(GuiResize(Size(1024, 768)))

            # Handle mode toggle
            gui = gui.event(KeyPressDown(KeyboardKey.GUI_MODE_TOGGLE))
            ```
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

        Renders all provided drawings to the game window, handling
        screen scaling and centering based on the current GUI
        configuration. Also renders debug log messages if available.

        Arguments:
            `draw_on_screens`: The drawings to render to the screen.

            `time_delta`: The time elapsed since the last update
                in milliseconds.

        Example:
            ```python
            from nextrpg import DrawOnScreen

            # Draw game elements
            drawings = (player_sprite, background, ui_elements)
            gui.draw(drawings, time_delta)
            ```
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

    def __post_init__(self) -> None:
        if not self._screen:
            init()
            font.init()

        self._update_title()
        self._update_screen()

    def _draw_log(self, time_delta: Millisecond) -> None:
        if msgs := pop_messages(time_delta):
            self._screen.blits(
                d.pygame for t in _log_text(msgs) for d in t.draw_on_screens
            )

    def _scale(self, draws: tuple[DrawOnScreen, ...]) -> DrawOnScreen:
        screen = Surface(self.initial_config.size)
        screen.blits(d.pygame for d in draws)
        scaled_drawing = Drawing(
            smoothscale(
                screen,
                self.initial_config.size.all_dimension_scale(self._scaling),
            )
        )
        return DrawOnScreen(self._center_shift, scaled_drawing)

    @cached_property
    def _scaling(self) -> float:
        current_width, current_height = self.current_config.size
        initial_width, initial_height = self.initial_config.size
        width_ratio = current_width / initial_width
        height_ratio = current_height / initial_height
        return min(width_ratio, height_ratio)

    @cached_property
    def _center_shift(self) -> Coordinate:
        current_width, current_height = self.current_config.size
        initial_width, initial_height = self.initial_config.size
        width_shift = (current_width - self._scaling * initial_width) / 2
        height_shift = (current_height - self._scaling * initial_height) / 2
        return Coordinate(width_shift, height_shift)

    @cached_property
    def _current_gui_flag(self) -> _GuiFlag:
        flag = DOUBLEBUF if self.current_config.double_buffer else 0
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
            or self.last_config.double_buffer
            != self.current_config.double_buffer
        ):
            screen = set_mode(self.current_config.size, self._current_gui_flag)
            object.__setattr__(self, "_screen", screen)

    @cached_property
    def _toggle_gui_mode(self) -> Self:
        updated_gui_mode = self.current_config.gui_mode.opposite
        updated_config = replace(self.current_config, gui_mode=updated_gui_mode)
        set_config(replace(config(), gui=updated_config))
        return replace(
            self, current_config=updated_config, last_config=self.current_config
        )

    def _resize(self, size: Size) -> Self:
        if size == self.current_config.size:
            return self
        updated_config = replace(self.current_config, size=size)
        set_config(replace(config(), gui=updated_config))
        return replace(
            self, current_config=updated_config, last_config=self.current_config
        )


def _log_text(
    msgs: tuple[ComponentAndMessage, ...],
) -> tuple[TextOnScreen, ...]:
    text_config = config().text
    spacing = text_config.line_spacing
    max_width = max(text_config.font.text_size(m.component).width for m in msgs)
    msg_spacing = max_width + 2 * spacing
    return tuple(
        text
        for i, (component, msg) in enumerate(msgs)
        for text in (
            TextOnScreen(Coordinate(spacing, _line_height(i)), Text(component)),
            TextOnScreen(Coordinate(msg_spacing, _line_height(i)), Text(msg)),
        )
    )


def _line_height(line_index: int) -> Pixel:
    spacing = config().text.line_spacing
    return spacing + line_index * (spacing + config().text.font.text_height)


type _GuiFlag = int
