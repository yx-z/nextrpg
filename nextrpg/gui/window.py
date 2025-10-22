import os
from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from typing import Self

from pygame.constants import SRCALPHA
from pygame.display import flip, set_caption, set_icon, set_mode
from pygame.surface import Surface

from nextrpg.config.config import config, set_config
from nextrpg.config.window_config import WindowConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.log import Log, LogEntry, MessageAndDrawing, pop_messages
from nextrpg.core.save import SaveIo
from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.drawing.animation_on_screen_like import AnimationOnScreenLike
from nextrpg.drawing.drawing import scale_surface
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.text import Text
from nextrpg.event.io_event import (
    IoEvent,
    KeyboardKey,
    KeyPressDown,
    WindowResize,
)
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size

log = Log()


@dataclass_with_default(frozen=True)
class Window:
    _: KW_ONLY = private_init_below()
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
    ___: None = default(lambda self: set_caption(self.current_config.title))
    ____: None = default(
        lambda self: (
            set_icon(icon.pygame)
            if (icon := self.current_config.icon)
            else None
        )
    )
    _screen: Surface = default(
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

    def event(self, e: IoEvent) -> Self:
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
        drawing_on_screens: tuple[DrawingOnScreen, ...],
        time_delta: Millisecond,
    ) -> None:
        log.debug(
            t"Size {self.current_config.size} Shift {self._center_shift}",
            duration=None,
        )
        self._screen.fill(self.current_config.background)

        if msgs := pop_messages(time_delta):
            drawing_on_screens += _log(msgs)
        base = Surface(self.initial_config.size, SRCALPHA)
        base.blits(d.pygame for d in drawing_on_screens)
        scaled = scale_surface(base, self._scaling)
        self._screen.blit(scaled, self._center_shift)
        flip()

    def _toggle_include_fps_in_window_title(self) -> Self:
        window_config = replace(
            self.current_config,
            include_fps_in_window_title=not self.current_config.include_fps_in_window_title,
        )
        _set_window_config(window_config)
        return self.tick()

    def _set_screen(self, cfg: WindowConfig) -> Surface:
        return set_mode(cfg.size, cfg.flag)

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
        _set_window_config(updated_config)
        return self.tick()

    def _resize(self, size: Size) -> Self:
        if size == self.current_config.size:
            return self
        updated_config = replace(self.current_config, size=size)
        _set_window_config(updated_config)
        return self.tick()

    @cached_property
    def _saved_config(self) -> WindowConfig | None:
        if (
            saved_config := SaveIo().update(self.initial_config)
        ) == self.initial_config:
            return None
        _set_window_config(saved_config)
        return saved_config


def _set_window_config(window_config: WindowConfig) -> None:
    SaveIo().save(window_config)
    full_config = replace(config(), window=window_config)
    set_config(full_config)


def _log(entries: tuple[LogEntry, ...]) -> tuple[DrawingOnScreen, ...]:
    assert (debug := config().debug)

    log_levels = tuple(Text(e.level.name) for e in entries)
    log_level_width = max(t.width for t in log_levels)

    components = tuple(Text(e.component) for e in entries)
    component_width = max(t.width for t in components)

    width_spacing = debug.log_width_spacing
    height_spacing = debug.log_height_spacing

    height = height_spacing
    res: list[DrawingOnScreen] = []
    for log_level, component, entry in zip(log_levels, components, entries):
        if isinstance(content := entry.log, MessageAndDrawing):
            drawing = content.drawing
            message = Text(content.message)
            height_spacing = max(height_spacing, message.height, drawing.height)
        else:
            drawing = None
            message = Text(content)
            height_spacing = max(height_spacing, message.height)
        height += max(log_level.height, component.height) + height_spacing
        log_level_coordinate = (width_spacing * height).coordinate
        res += log_level.drawing_on_screens(log_level_coordinate)

        component_coordinate = (
            log_level_coordinate + log_level_width + width_spacing
        )
        res += component.drawing_on_screens(component_coordinate)

        message_coordinate = (
            component_coordinate + component_width + width_spacing
        )
        message_drawing_on_screens = message.drawing_on_screens(
            message_coordinate
        )
        res += message_drawing_on_screens

        if isinstance(drawing, AnimationOnScreenLike):
            drawing_on_screens = drawing.drawing_on_screens
        elif isinstance(drawing, AnimationLike):
            drawing_coordinate = (
                message_coordinate + message.width + width_spacing
            )
            drawing_on_screens = drawing.drawing_on_screens(drawing_coordinate)
        else:
            drawing_on_screens = []
        res += drawing_on_screens

    return tuple(res)
