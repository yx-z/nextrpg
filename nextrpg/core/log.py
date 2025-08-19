from dataclasses import dataclass, field, replace
from inspect import stack
from pathlib import Path
from string.templatelib import Interpolation, Template
from typing import NamedTuple

from nextrpg.core.time import Millisecond, Timer
from nextrpg.global_config.debug_config import LogLevel


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

    def warning(
        self,
        message: Template | str,
        *,
        duration: Millisecond | _DurationFromConfig | None = _FROM_CONFIG,
    ) -> None:
        _add(self.component, LogLevel.WARNING, message, duration)

    def error(
        self,
        message: Template | str,
        *,
        duration: Millisecond | _DurationFromConfig | None = _FROM_CONFIG,
    ) -> None:
        _add(self.component, LogLevel.ERROR, message, duration)


class ComponentAndMessage(NamedTuple):
    component: str
    message: str


def pop_messages(time_delta: Millisecond) -> tuple[ComponentAndMessage, ...]:
    from nextrpg.global_config.global_config import config

    if not (debug := config().debug):
        _pop(time_delta)
        return ()

    msgs = tuple(
        ComponentAndMessage(e.component, e.formatted)
        for e in _entries + list(_timed_entries.values())
        if e.level >= debug.log_level
    )
    _pop(time_delta)
    return msgs


@dataclass(frozen=True)
class _Key:
    component: str
    template: tuple[str, ...]


@dataclass(frozen=True)
class _LogEntry:
    component: str
    level: LogLevel
    message: Template

    @property
    def formatted(self) -> str:
        return "".join(_format(m) for m in self.message)


@dataclass(frozen=True)
class _TimedLogEntry(_LogEntry):
    timer: Timer


def _pop(time_delta: Millisecond) -> None:
    _entries.clear()
    global _timed_entries
    _timed_entries = {
        k: replace(v, timer=timer)
        for k, v in _timed_entries.items()
        if not (timer := v.timer.tick(time_delta)).complete
    }


def _add(
    component: str,
    level: LogLevel,
    message: Template | str,
    duration: Millisecond | _DurationFromConfig | None,
) -> None:
    from nextrpg.global_config.global_config import config

    if not (debug := config().debug) or debug.log_level > level:
        return
    message = Template(message) if isinstance(message, str) else message
    if duration is None:
        _entries.append(_LogEntry(component, level, message))
        return
    duration = debug.log_duration if duration is _FROM_CONFIG else duration
    if (k := _Key(component, message.strings)) not in _timed_entries:
        _timed_entries[k] = _TimedLogEntry(
            component, level, message, Timer(duration)
        )


def _format(s: Interpolation | str) -> str:
    if isinstance(s, Interpolation):
        return format(s.value, s.format_spec)
    return s


_entries: list[_LogEntry] = []
_timed_entries: dict[_Key, _TimedLogEntry] = {}
