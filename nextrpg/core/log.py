import logging
from dataclasses import dataclass, field, replace
from functools import cached_property
from inspect import stack
from logging import Logger
from pathlib import Path
from string.templatelib import Interpolation, Template
from typing import TYPE_CHECKING

from nextrpg.config.system.debug_config import LogLevel
from nextrpg.core.time import Millisecond, Timer

if TYPE_CHECKING:
    from nextrpg.drawing.animation_like import AnimationLike
    from nextrpg.drawing.animation_on_screen_like import AnimationOnScreenLike


class _DurationFromConfig:
    pass


_FROM_CONFIG = _DurationFromConfig()


def _log_name() -> str:
    file = Path(stack()[2].filename)
    # "file.py" -> "file"
    return file.name.split(".")[0]


@dataclass(frozen=True)
class Log:
    component: str = field(default_factory=_log_name)

    def debug(
        self,
        message: Template | str,
        *,
        duration: Millisecond | _DurationFromConfig | None = _FROM_CONFIG,
    ) -> None:
        _add(self.component, LogLevel.DEBUG, message, duration)

    def info(
        self,
        message: Template | str,
        *,
        duration: Millisecond | _DurationFromConfig | None = _FROM_CONFIG,
    ) -> None:
        _add(self.component, LogLevel.INFO, message, duration)

    def error(
        self,
        message: Template | str,
        *,
        duration: Millisecond | _DurationFromConfig | None = _FROM_CONFIG,
    ) -> None:
        _add(self.component, LogLevel.ERROR, message, duration)

    def debug_drawing(
        self,
        keyed_drawings: (
            dict[str, AnimationLike | AnimationOnScreenLike] | None
        ) = None,
        *,
        duration: Millisecond | _DurationFromConfig | None = _FROM_CONFIG,
        **kwargs: AnimationLike | AnimationOnScreenLike,
    ) -> None:
        drawings = (keyed_drawings or {}) | kwargs
        _add_drawings(self.component, LogLevel.DEBUG, duration, drawings)

    def info_drawing(
        self,
        keyed_drawings: (
            dict[str, AnimationLike | AnimationOnScreenLike] | None
        ) = None,
        *,
        duration: Millisecond | _DurationFromConfig | None = _FROM_CONFIG,
        **kwargs: AnimationLike | AnimationOnScreenLike,
    ) -> None:
        drawings = (keyed_drawings or {}) | kwargs
        _add_drawings(self.component, LogLevel.INFO, duration, drawings)

    def error_drawing(
        self,
        keyed_drawings: (
            dict[str, AnimationLike | AnimationOnScreenLike] | None
        ) = None,
        *,
        duration: Millisecond | _DurationFromConfig | None = _FROM_CONFIG,
        **kwargs: AnimationLike | AnimationOnScreenLike,
    ) -> None:
        drawings = (keyed_drawings or {}) | kwargs
        _add_drawings(self.component, LogLevel.ERROR, duration, drawings)


@dataclass(frozen=True)
class MessageKeyAndDrawing:
    message_key: str
    drawing: AnimationLike | AnimationOnScreenLike


@dataclass(frozen=True)
class LogEntry:
    component: str
    level: LogLevel
    message: Template | MessageKeyAndDrawing

    @cached_property
    def formatted(self) -> str | MessageKeyAndDrawing:
        if isinstance(self.message, MessageKeyAndDrawing):
            return self.message
        formatted = tuple(_format(m) for m in self.message)
        return "".join(formatted)


def pop_messages(time_delta: Millisecond) -> list[LogEntry]:
    from nextrpg.config.config import config

    if not (debug := config().debug):
        _pop(time_delta)
        return []

    msgs = [
        e
        for e in _entries + list(_timed_entries.values())
        if e.component not in debug.exclude_loggers
        and e.level >= debug.log_level
    ]
    _pop(time_delta)
    return msgs


def console(name: str | None = None) -> Logger:
    log_name = name or _log_name()
    return logging.getLogger(log_name)


@dataclass(frozen=True)
class _Key:
    component: str
    template: list[str] | str


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

    if not (debug := config().debug) or debug.log_level > level:
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
        timer_duration = debug.log_duration
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


def _add_drawings(
    component: str,
    level: LogLevel,
    duration: Millisecond | _DurationFromConfig | None,
    kwargs: dict[str, AnimationLike | AnimationOnScreenLike],
) -> None:
    for key, drawing in kwargs.items():
        message_and_drawing = MessageKeyAndDrawing(key, drawing)
        _add(component, level, message_and_drawing, duration)


_entries: list[LogEntry] = []
_timed_entries: dict[_Key, _TimedLogEntry] = {}
