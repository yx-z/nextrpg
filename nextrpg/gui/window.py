from __future__ import annotations

import os
from dataclasses import KW_ONLY, dataclass, field, replace
from functools import cached_property
from typing import Self

from pygame import DOUBLEBUF, font
from pygame.display import flip, init, set_caption, set_icon, set_mode
from pygame.locals import FULLSCREEN, RESIZABLE
from pygame.surface import Surface
from pygame.transform import smoothscale

from nextrpg.core.coordinate import Coordinate, ORIGIN
from nextrpg.core.dataclass_with_init import not_constructor_below
from nextrpg.core.dimension import Size, WidthAndHeightScaling
from nextrpg.core.logger import ComponentAndMessage, Logger, pop_messages
from nextrpg.core.save import save_io
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw import Draw, DrawOnScreen
from nextrpg.draw.text import Text
from nextrpg.draw.text_on_screen import TextOnScreen
from nextrpg.event.pygame_event import (
    GuiResize,
    KeyPressDown,
    KeyboardKey,
    PygameEvent,
)
from nextrpg.global_config.global_config import config, set_config
from nextrpg.global_config.gui_config import GuiConfig, GuiMode, ResizeMode

logger = Logger()


@dataclass(frozen=True)
class Window:
    _: KW_ONLY = not_constructor_below()
    current_config: GuiConfig = field(default_factory=lambda: config().gui)
    last_config: GuiConfig = field(default_factory=lambda: config().gui)
    initial_config: GuiConfig = field(default_factory=lambda: config().gui)
    _screen: Surface | None = None
    _title: str | None = None
    _icon: Draw | None = None

    def update(self) -> Self:
        if config().gui is self.current_config:
            return self
        return replace(
            self, current_config=config().gui, last_config=self.current_config
        )

    def event(self, e: PygameEvent) -> Self:
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
        logger.debug(
            t"Size {self.current_config.size} Shift {self._center_shift}",
            duration=None,
        )
        self._screen.fill(self.current_config.background.tuple)

        if msgs := pop_messages(time_delta):
            draw_on_screens += tuple(
                d for text in _log_text(msgs) for d in text.draw_on_screens
            )

        match self.current_config.resize_mode:
            case ResizeMode.SCALE:
                self._screen.blit(*self._scale(draw_on_screens).pygame)
            case ResizeMode.KEEP_NATIVE_SIZE:
                self._screen.blits(d.pygame for d in draw_on_screens)
        flip()

    def __post_init__(self) -> None:
        os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
        if not self._screen:
            init()
            font.init()

        if self.current_config.icon and (
            self._icon is None
            or self.current_config.icon != self.last_config.icon
        ):
            icon = Draw(self.current_config.icon)
            set_icon(icon.pygame)
            object.__setattr__(self, "_icon", icon)

        if (
            self._title is None
            or self.current_config.title != self.last_config.title
        ):
            object.__setattr__(self, "_title", self.current_config.title)
            set_caption(self._title)

        if (
            self._screen is None
            or self.last_config.size != self.current_config.size
            or self.last_config.gui_mode != self.current_config.gui_mode
            or self.last_config.allow_window_resize
            != self.current_config.allow_window_resize
            or self.last_config.double_buffer
            != self.current_config.double_buffer
        ):
            screen = set_mode(
                self.current_config.size.tuple, self._current_gui_flag
            )
            object.__setattr__(self, "_screen", screen)

        if gui := save_io().load(GuiConfig):
            set_config(replace(config(), gui=gui))

    def _scale(self, draws: tuple[DrawOnScreen, ...]) -> DrawOnScreen:
        screen = Surface(self.initial_config.size.tuple)
        screen.blits(d.pygame for d in draws)
        scaled = (self.initial_config.size * self._scaling).tuple
        scaled_draw = Draw(smoothscale(screen, scaled))
        return DrawOnScreen(self._center_shift, scaled_draw)

    @cached_property
    def _scaling(self) -> WidthAndHeightScaling:
        current_width, current_height = self.current_config.size
        initial_width, initial_height = self.initial_config.size
        width_ratio = current_width / initial_width.value
        height_ratio = current_height / initial_height.value
        return WidthAndHeightScaling(min(width_ratio, height_ratio))

    @cached_property
    def _center_shift(self) -> Coordinate:
        current_width, current_height = self.current_config.size
        initial_width, initial_height = self.initial_config.size
        width_shift = (current_width - self._scaling.value * initial_width) / 2
        height_shift = (
            current_height - self._scaling.value * initial_height
        ) / 2
        return Coordinate(width_shift, height_shift)

    @cached_property
    def _current_gui_flag(self) -> _GuiFlag:
        flag = DOUBLEBUF if self.current_config.double_buffer else 0
        if self.current_config.gui_mode is GuiMode.FULL_SCREEN:
            flag |= FULLSCREEN
        if self.current_config.allow_window_resize:
            flag |= RESIZABLE
        return flag

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
    components = Text("\n".join(m.component for m in msgs))
    components_on_screen = TextOnScreen(ORIGIN, components)
    msgs = Text("\n".join(m.message for m in msgs))
    msgs_on_screen = TextOnScreen(ORIGIN + components.width, msgs)
    return components_on_screen, msgs_on_screen


type _GuiFlag = int
