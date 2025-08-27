from __future__ import annotations

import os
from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from typing import Self

from pygame import SRCALPHA
from pygame.display import flip, set_caption, set_icon, set_mode
from pygame.surface import Surface

from nextrpg.config.config import config, set_config
from nextrpg.config.window_config import ResizeMode, WindowConfig
from nextrpg.core.dataclass_with_default_init import (
    dataclass_with_default_init,
    default_init,
    not_constructor_below,
)
from nextrpg.core.log import ComponentAndMessage, Log, pop_messages
from nextrpg.core.save import SaveIo
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.draw.text import Text
from nextrpg.draw.text_on_screen import TextOnScreen
from nextrpg.event.pygame_event import (
    KeyboardKey,
    KeyPressDown,
    PygameEvent,
    WindowResize,
)
from nextrpg.geometry.coordinate import ORIGIN, Coordinate
from nextrpg.geometry.dimension import Size

log = Log()


@dataclass_with_default_init(frozen=True)
class Window:
    _: KW_ONLY = not_constructor_below()
    initial_config: WindowConfig = field(
        default_factory=lambda: config().window
    )
    last_config: WindowConfig = default_init(lambda self: self.initial_config)
    current_config: WindowConfig = default_init(
        lambda self: self._saved_config or self.initial_config
    )
    __: None = field(
        default_factory=lambda: os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
    )
    ___: None = default_init(
        lambda self: set_caption(self.current_config.title)
    )
    ____: None = default_init(
        lambda self: (
            set_icon(icon.pygame)
            if (icon := self.current_config.icon)
            else None
        )
    )
    _screen: Surface = default_init(
        lambda self: self._set_screen(self.current_config)
    )

    def tick(self, fps_info: str | None = None) -> Self:
        updated_config = config().window
        if updated_config.include_fps_in_window_title and fps_info:
            set_caption(f"{config().window.title} {fps_info}")
        if (
            self.current_config.include_fps_in_window_title
            and not updated_config.include_fps_in_window_title
        ):
            set_caption(config().window.title)

        if updated_config is self.current_config:
            return self

        if not updated_config.need_new_screen(self.current_config):
            return replace(
                self,
                current_config=updated_config,
                last_config=self.current_config,
            )

        screen = self._set_screen(updated_config)
        return replace(
            self,
            current_config=updated_config,
            last_config=self.current_config,
            _screen=screen,
        )

    def event(self, e: PygameEvent) -> Self:
        match e:
            case WindowResize():
                return self._resize(e.size)
            case KeyPressDown():
                if e.key is KeyboardKey.FULL_SCREEN_TOGGLE:
                    return self._toggle_full_screen()
                if e.key is KeyboardKey.INCLUDE_FPS_IN_WINDOW_TITLE_TOGGLE:
                    return self._toggle_include_fps_in_window_title()
        return self

    def blits(
        self,
        drawing_on_screens: list[DrawingOnScreen],
        time_delta: Millisecond,
    ) -> None:
        log.debug(
            t"Size {self.current_config.size} Shift {self._center_shift}",
            duration=None,
        )
        self._screen.fill(self.current_config.background)

        if msgs := pop_messages(time_delta):
            drawing_on_screens += tuple(
                d for text in _log_text(msgs) for d in text.drawing_on_screens
            )

        match self.current_config.resize:
            case ResizeMode.SCALE:
                self._screen.blit(*self._scale(drawing_on_screens).pygame)
            case ResizeMode.KEEP_NATIVE_SIZE:
                drawing_on_screens = tuple(d.pygame for d in drawing_on_screens)
                self._screen.blits(drawing_on_screens)
        flip()

    def _toggle_include_fps_in_window_title(self) -> Self:
        window_config = replace(
            self.current_config,
            include_fps_in_window_title=not self.current_config.include_fps_in_window_title,
        )
        full_config = replace(config(), window=window_config)
        set_config(full_config)
        return self.tick()

    def _set_screen(self, cfg: WindowConfig) -> Surface:
        return set_mode(cfg.size, cfg.flag)

    def _scale(
        self, drawing_on_screens: list[DrawingOnScreen]
    ) -> DrawingOnScreen:
        screen = Surface(self.initial_config.size, SRCALPHA)
        surfaces = tuple(d.pygame for d in drawing_on_screens)
        screen.blits(surfaces)
        scaled_draw = Drawing(screen) * self._scaling
        return DrawingOnScreen(self._center_shift, scaled_draw)

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

    def _toggle_full_screen(self) -> Self:
        full_screen = not self.current_config.full_screen
        updated_config = replace(self.current_config, full_screen=full_screen)
        full_config = replace(config(), window=updated_config)
        set_config(full_config)
        return self.tick()

    def _resize(self, size: Size) -> Self:
        if size == self.current_config.size:
            return self
        updated_config = replace(self.current_config, size=size)
        full_config = replace(config(), window=updated_config)
        set_config(full_config)
        return self.tick()

    @cached_property
    def _saved_config(self) -> WindowConfig | None:
        saved_config = SaveIo().update(self.initial_config)
        if saved_config == self.initial_config:
            return None
        full_config = replace(config(), window=saved_config)
        set_config(full_config)
        return saved_config


def _log_text(
    component_and_messages: tuple[ComponentAndMessage, ...],
) -> tuple[TextOnScreen, ...]:
    components = tuple(m.component for m in component_and_messages)
    component_text = Text("\n".join(components))
    components_on_screen = TextOnScreen(ORIGIN, component_text)

    messages = tuple(m.message for m in component_and_messages)
    msg_text = Text("\n".join(messages))
    msgs_on_screen = TextOnScreen(ORIGIN + component_text.width, msg_text)
    return components_on_screen, msgs_on_screen
