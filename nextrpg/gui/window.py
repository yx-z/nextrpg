import os
from collections.abc import Collection, Iterable
from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from itertools import chain
from typing import Self

from pygame import SRCALPHA, Surface
from pygame.display import flip, set_caption, set_icon, set_mode

from nextrpg.config.config import config, set_config
from nextrpg.config.system.key_mapping_config import KeyMappingConfig
from nextrpg.config.system.window_config import WindowConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.logger import (
    LogEntry,
    Logger,
    MessageKeyAndDrawing,
    pop_messages,
)
from nextrpg.core.save import SaveIo
from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.drawing_on_screens import (
    DrawingOnScreens,
    drawing_on_screens,
)
from nextrpg.drawing.sprite_on_screen import SpriteOnScreen
from nextrpg.drawing.text import Text
from nextrpg.event.base_event import BaseEvent
from nextrpg.event.io_event import (
    MouseButtonDown,
    WindowResize,
    is_key_press,
)
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import ValueScaling
from nextrpg.geometry.scaling import WidthAndHeightScaling
from nextrpg.geometry.size import ZERO_HEIGHT, Size

logger = Logger("window")


@dataclass_with_default(frozen=True)
class Window:
    _: KW_ONLY = private_init_below()
    initial_config: WindowConfig = field(
        default_factory=lambda: config().system.window
    )
    last_config: WindowConfig = default(lambda self: self.initial_config)
    current_config: WindowConfig = default(
        lambda self: self._saved_config or self.initial_config
    )
    _screen: Surface = default(
        lambda self: self._set_screen(self.current_config)
    )

    def __post_init__(self) -> None:
        os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
        set_caption(self.current_config.title)
        if icon := self.current_config.icon:
            set_icon(icon.drawing.pygame)

    def tick(self, fps: str | None = None) -> Self:
        updated_config = config().system.window
        title = updated_config.title
        if updated_config.include_fps_in_window_title and fps:
            set_caption(f"{title} {fps}")
        elif (
            self.current_config.include_fps_in_window_title
            and not updated_config.include_fps_in_window_title
        ):
            set_caption(title)

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

    def event(self, event: BaseEvent) -> Self:
        if is_key_press(event, KeyMappingConfig.full_screen_toggle):
            return self.toggle_full_screen()
        if is_key_press(event, KeyMappingConfig.include_fps_in_title_toggle):
            return self.toggle_include_fps_in_window_title()
        if isinstance(event, WindowResize):
            return self.resize(event.size)
        if isinstance(event, MouseButtonDown):
            logger.debug(f"Mouse clicked at {event.coordinate}")
        return self

    def blits(
        self, drawing_on_screens: DrawingOnScreens, time_delta: Millisecond
    ) -> None:
        logger.debug(
            f"Size {self.current_config.size} Shift {self._center_shift}",
            duration=None,
        )
        self._screen.fill(self.current_config.background.pygame)

        base = Surface(self.initial_config.size, SRCALPHA).convert_alpha()
        base.blits(d.pygame for d in drawing_on_screens)
        scaled = Drawing(base) * WidthAndHeightScaling(self._scaling)
        self._screen.blit(scaled.pygame, self._center_shift)
        if msgs := pop_messages(time_delta):
            logs = _log(msgs)
            self._screen.blits(d.pygame for d in logs)
        flip()

    def toggle_full_screen(self) -> Self:
        full_screen = not self.current_config.full_screen
        updated_config = replace(self.current_config, full_screen=full_screen)
        _set_window_config(updated_config)
        return self.tick()

    def resize(self, size: Size) -> Self:
        if size == self.current_config.size:
            return self
        updated_config = replace(self.current_config, size=size)
        _set_window_config(updated_config)
        return self.tick()

    def toggle_include_fps_in_window_title(self) -> Self:
        window_config = replace(
            self.current_config,
            include_fps_in_window_title=not self.current_config.include_fps_in_window_title,
        )
        _set_window_config(window_config)
        return self.tick()

    def _set_screen(self, cfg: WindowConfig) -> Surface:
        return set_mode(cfg.size, cfg.flag)

    @cached_property
    def _scaling(self) -> ValueScaling:
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
    def _saved_config(self) -> WindowConfig | None:
        if (
            saved_config := SaveIo().update(self.initial_config)
        ) == self.initial_config:
            return None
        _set_window_config(saved_config)
        return saved_config


def _set_window_config(window_config: WindowConfig) -> None:
    SaveIo().save(window_config)
    current_config = config()
    system_config = replace(current_config.system, window=window_config)
    cfg = replace(current_config, system=system_config)
    set_config(cfg)


def _log(entries: Collection[LogEntry]) -> Iterable[DrawingOnScreen]:
    debug = config().debug
    assert debug, f"Expect DebugConfig"
    logging_config = debug.logging
    assert logging_config, f"Expect LoggingConfig"
    text_config = logging_config.text

    components = tuple(Text(e.component, text_config) for e in entries)
    component_width = max(t.width for t in components)

    height = ZERO_HEIGHT
    res: list[DrawingOnScreen] = []
    for component, entry in zip(components, entries):
        if isinstance(content := entry.formatted, MessageKeyAndDrawing):
            drawing = content.drawing
            message = Text(f" {content.message_key} = ", text_config)
            line_height = max(message.height, drawing.height)
        else:
            drawing = None
            message = Text(f" {content}", text_config)
            line_height = message.height
        component_coordinate = height.y_axis.coordinate
        res += component.drawing_on_screens(component_coordinate)

        message_coordinate = component_coordinate + component_width
        res += message.drawing_on_screens(message_coordinate)

        if drawing:
            if isinstance(drawing, SpriteOnScreen):
                # Shift its drawings to log area.
                drawing = drawing.drawing_group_at_origin
            res += drawing.drawing_on_screens(
                message_coordinate + message.size, Anchor.BOTTOM_LEFT
            )
        height += max(line_height, component.height)

    if (
        (debug := config().debug)
        and (logging_config := debug.logging)
        and (color := logging_config.background_color)
    ):
        drawing_on_screen = drawing_on_screens(res)
        background = drawing_on_screen.rectangle_area_on_screen.fill(color)
        return chain((background,), res)
    return res
