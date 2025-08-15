from __future__ import annotations

import os
from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from typing import Self

from pygame import font
from pygame.display import flip, init, set_caption, set_icon, set_mode
from pygame.locals import FULLSCREEN, RESIZABLE
from pygame.surface import Surface
from pygame.transform import smoothscale

from nextrpg.core.coordinate import Coordinate, ORIGIN
from nextrpg.core.dataclass_with_init import (
    dataclass_with_init,
    default,
    not_constructor_below,
)
from nextrpg.core.dimension import Size, WidthAndHeightScaling
from nextrpg.core.log import ComponentAndMessage, Log, pop_messages
from nextrpg.core.save import SaveIo
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw import Draw, DrawOnScreen
from nextrpg.draw.text import Text
from nextrpg.draw.text_on_screen import TextOnScreen
from nextrpg.event.pygame_event import (
    KeyPressDown,
    KeyboardKey,
    PygameEvent,
    WindowResize,
)
from nextrpg.global_config.global_config import config, set_config
from nextrpg.global_config.window_config import (
    ResizeMode,
    WindowConfig,
    WindowMode,
)

log = Log()


@dataclass_with_init(frozen=True)
class Window:
    _: KW_ONLY = not_constructor_below()
    initial_config: WindowConfig = field(
        default_factory=lambda: config().window
    )
    last_config: WindowConfig = default(lambda self: self.initial_config)
    current_config: WindowConfig = default(
        lambda self: self._saved_config or self.initial_config
    )
    __: None = field(
        default_factory=lambda: os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
    )
    _screen: Surface = default(
        lambda self: self._set_screen(self.current_config)
    )

    def update(self) -> Self:
        if (updated_config := config().window) is self.current_config:
            return self

        if (
            updated_config.size != self.current_config.size
            or updated_config.mode != self.current_config.mode
        ):
            screen = self._set_screen(updated_config)
        else:
            screen = self._screen

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
                if e.key is KeyboardKey.WINDOW_MODE_TOGGLE:
                    return self._toggle_mode
        return self

    def draw(
        self, draw_on_screens: tuple[DrawOnScreen, ...], time_delta: Millisecond
    ) -> None:
        log.debug(
            t"Size {self.current_config.size} Shift {self._center_shift}",
            duration=None,
        )
        self._screen.fill(self.current_config.background.tuple)

        if msgs := pop_messages(time_delta):
            draw_on_screens += tuple(
                d for text in _log_text(msgs) for d in text.draw_on_screens
            )

        match self.current_config.resize:
            case ResizeMode.SCALE:
                self._screen.blit(*self._scale(draw_on_screens).pygame)
            case ResizeMode.KEEP_NATIVE_SIZE:
                self._screen.blits(d.pygame for d in draw_on_screens)
        flip()

    def _set_screen(self, cfg: WindowConfig) -> Surface:
        if cfg is self.initial_config or cfg is self._saved_config:
            init()
            font.init()
            set_caption(cfg.title)
            if cfg.icon:
                icon = Draw(cfg.icon)
                set_icon(icon.pygame)
        return set_mode(cfg.size.tuple, self._window_flag(cfg))

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

    def _window_flag(self, cfg: WindowConfig) -> _WindowFlag:
        flag = cfg.double_buffer
        if cfg.mode is WindowMode.FULL_SCREEN:
            flag |= FULLSCREEN
        if cfg.allow_resize:
            flag |= RESIZABLE
        return flag

    @cached_property
    def _toggle_mode(self) -> Self:
        mode = self.current_config.mode.opposite
        updated_config = replace(self.current_config, mode=mode)
        full_config = replace(config(), window=updated_config)
        set_config(full_config)
        return self.update()

    def _resize(self, size: Size) -> Self:
        if size == self.current_config.size:
            return self
        updated_config = replace(self.current_config, size=size)
        full_config = replace(config(), window=updated_config)
        set_config(full_config)
        return self.update()

    @cached_property
    def _saved_config(self) -> WindowConfig | None:
        saved_config = SaveIo().update(self.initial_config)
        if (
            saved_config.size != self.initial_config.size
            or saved_config.mode != self.initial_config.mode
        ):
            full_config = replace(config(), window=saved_config)
            set_config(full_config)
            return saved_config
        return None


def _log_text(
    msgs: tuple[ComponentAndMessage, ...],
) -> tuple[TextOnScreen, ...]:
    components = Text("\n".join(m.component for m in msgs))
    components_on_screen = TextOnScreen(ORIGIN, components)
    msgs = Text("\n".join(m.message for m in msgs))
    msgs_on_screen = TextOnScreen(ORIGIN + components.width, msgs)
    return components_on_screen, msgs_on_screen


type _WindowFlag = int
