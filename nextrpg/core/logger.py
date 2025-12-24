import logging
from dataclasses import dataclass, replace
from functools import cached_property
from string.templatelib import Interpolation, Template
from typing import TYPE_CHECKING, Any

from nextrpg.config.logging_config import LogLevel
from nextrpg.core.time import Millisecond, Timer

if TYPE_CHECKING:
    from nextrpg.drawing.sprite import Sprite
    from nextrpg.drawing.sprite_on_screen import SpriteOnScreen


class _DurationFromConfig:
    pass


_FROM_CONFIG = _DurationFromConfig()


@dataclass(frozen=True)
class Logger:
    component: str

    def debug(
        self,
        message: Template | str,
        console_logger: logging.Logger | None = None,
        *,
        duration: Millisecond | _DurationFromConfig | None = _FROM_CONFIG,
    ) -> None:
        if console_logger:
            console_logger.debug(message)
        _add(self.component, LogLevel.DEBUG, message, duration)

    def info(
        self,
        message: Template | str,
        console_logger: logging.Logger | None = None,
        *,
        duration: Millisecond | _DurationFromConfig | None = _FROM_CONFIG,
    ) -> None:
        if console_logger:
            console_logger.info(message)
        _add(self.component, LogLevel.INFO, message, duration)

    def error(
        self,
        message: Template | str,
        console_logger: logging.Logger | None = None,
        *,
        duration: Millisecond | _DurationFromConfig | None = _FROM_CONFIG,
    ) -> None:
        if console_logger:
            console_logger.error(message)
        _add(self.component, LogLevel.ERROR, message, duration)

    def debug_drawing(
        self,
        keyed_drawings: dict[Any, Sprite | SpriteOnScreen] | None = None,
        *,
        duration: Millisecond | _DurationFromConfig | None = _FROM_CONFIG,
        **kwargs: Sprite | SpriteOnScreen,
    ) -> None:
        drawings = (keyed_drawings or {}) | kwargs
        _add_drawings(self.component, LogLevel.DEBUG, duration, drawings)

    def info_drawing(
        self,
        keyed_drawings: dict[Any, Sprite | SpriteOnScreen] | None = None,
        *,
        duration: Millisecond | _DurationFromConfig | None = _FROM_CONFIG,
        **kwargs: Sprite | SpriteOnScreen,
    ) -> None:
        drawings = (keyed_drawings or {}) | kwargs
        _add_drawings(self.component, LogLevel.INFO, duration, drawings)

    def error_drawing(
        self,
        keyed_drawings: dict[Any, Sprite | SpriteOnScreen] | None = None,
        *,
        duration: Millisecond | _DurationFromConfig | None = _FROM_CONFIG,
        **kwargs: Sprite | SpriteOnScreen,
    ) -> None:
        drawings = (keyed_drawings or {}) | kwargs
        _add_drawings(self.component, LogLevel.ERROR, duration, drawings)


@dataclass(frozen=True)
class MessageKeyAndDrawing:
    message_key: Any
    drawing: Sprite | SpriteOnScreen


@dataclass(frozen=True)
class LogEntry:
    component: str
    level: LogLevel
    message: Template | MessageKeyAndDrawing

    @cached_property
    def formatted(self) -> str | MessageKeyAndDrawing:
        if isinstance(self.message, MessageKeyAndDrawing):
            return self.message
        return _format_template(self.message)


def pop_messages(time_delta: Millisecond) -> tuple[LogEntry, ...]:
    from nextrpg.config.config import config

    if not (debug := config().debug) or not (logging_config := debug.logging):
        _pop(time_delta)
        return ()

    msgs = tuple(
        e
        for e in _entries + list(_timed_entries.values())
        if e.component not in logging_config.exclude_on_screen_loggers
        and e.level >= logging_config.level
    )
    _pop(time_delta)
    return msgs


@dataclass(frozen=True)
class _Key:
    component: str
    template: tuple[str, ...] | Any


@dataclass(frozen=True)
class _TimedLogEntry(LogEntry):
    timer: Timer


def _pop(time_delta: Millisecond) -> None:
    _entries.clear()
    global _timed_entries
    _timed_entries = {
        k: replace(v, timer=timer)
        for k, v in _timed_entries.items()
        if not (timer := v.timer.tick(time_delta)).is_complete
    }


def _add(
    component: str,
    level: LogLevel,
    message: Template | str | MessageKeyAndDrawing,
    duration: Millisecond | _DurationFromConfig | None,
) -> None:
    from nextrpg.config.config import config

    if (
        not (debug := config().debug)
        or not (logging_config := debug.logging)
        or logging_config.level > level
    ):
        return

    if isinstance(message, str):
        msg = Template(message)
    else:
        msg = message

    if duration is None:
        log_entry = LogEntry(component, level, msg)
        _entries.append(log_entry)
        return

    if duration is _FROM_CONFIG:
        timer_duration = logging_config.default_on_screen_duration
    else:
        assert isinstance(duration, int)
        timer_duration = duration
    timer = Timer(timer_duration)

    if isinstance(msg, MessageKeyAndDrawing):
        msg_key = msg.message_key
    else:
        msg_key = msg.strings
    if (k := _Key(component, msg_key)) not in _timed_entries:
        _timed_entries[k] = _TimedLogEntry(component, level, msg, timer)


def _format(s: Interpolation | str) -> str:
    if isinstance(s, Interpolation):
        return format(s.value, s.format_spec)
    return s


def _format_template(s: Template) -> str:
    return "".join(_format(m) for m in s)


def _add_drawings(
    component: str,
    level: LogLevel,
    duration: Millisecond | _DurationFromConfig | None,
    kwargs: dict[str, Sprite | SpriteOnScreen],
) -> None:
    for key, drawing in kwargs.items():
        message_and_drawing = MessageKeyAndDrawing(key, drawing)
        _add(component, level, message_and_drawing, duration)


_entries: list[LogEntry] = []
_timed_entries: dict[_Key, _TimedLogEntry] = {}
