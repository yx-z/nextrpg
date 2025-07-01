from dataclasses import dataclass, replace
from functools import cached_property
from itertools import chain
from string.templatelib import Interpolation, Template
from typing import NamedTuple

from nextrpg.config import LogLevel, config
from nextrpg.core import Millisecond, Timer


class DurationFromConfig:
    pass


FROM_CONFIG = DurationFromConfig()


@dataclass
class Logger:
    component: str

    def debug(
        self,
        message: Template,
        *,
        duration: Millisecond | DurationFromConfig | None = None,
    ) -> None:
        _add(self.component, LogLevel.DEBUG, message, duration)

    def info(
        self,
        message: Template,
        *,
        duration: Millisecond | DurationFromConfig | None = None,
    ) -> None:
        _add(self.component, LogLevel.INFO, message, duration)

    def warning(
        self,
        message: Template,
        *,
        duration: Millisecond | DurationFromConfig | None = None,
    ) -> None:
        _add(self.component, LogLevel.WARNING, message, duration)

    def error(
        self,
        message: Template,
        *,
        duration: Millisecond | DurationFromConfig | None = None,
    ) -> None:
        _add(self.component, LogLevel.ERROR, message, duration)

    def __new__(cls, component: str) -> Logger:
        if component in _instances:
            raise ValueError(
                f"Logger {component=} already exists."
                f"Use another name for better log separation."
            )

        instance = super().__new__(cls)
        _instances[component] = instance
        return instance


class ComponentAndMessage(NamedTuple):
    component: str
    message: str


def pop_messages(time_delta: Millisecond) -> list[ComponentAndMessage]:
    if not (debug := config().debug):
        _pop(time_delta)
        return []
    msgs = [
        ComponentAndMessage(e.component, e.formatted)
        for e in chain(_entries, _timed_entries.values())
        if e.level >= debug.log_level
    ]
    _pop(time_delta)
    return msgs


class _Key(NamedTuple):
    component: str
    template: tuple[str, ...]


@dataclass
class _LogEntry:
    component: str
    level: LogLevel
    message: Template

    @cached_property
    def formatted(self) -> str:
        return "".join(map(_format, self.message))


@dataclass
class _TimedLogEntry(_LogEntry):
    timer: Timer


def _pop(time_delta: Millisecond) -> None:
    _entries.clear()
    global _timed_entries
    _timed_entries = {
        k: t
        for k, v in _timed_entries.items()
        if not (t := replace(v, timer=v.timer.tick(time_delta))).timer.expired
    }


def _add(
    component: str,
    level: LogLevel,
    message: Template,
    duration: Millisecond | DurationFromConfig | None,
) -> None:
    if not (debug := config().debug):
        return
    if duration is None:
        _entries.append(_LogEntry(component, level, message))
        return
    duration = debug.log_duration if duration is FROM_CONFIG else duration
    if (k := _Key(component, message.strings)) not in _timed_entries:
        _timed_entries[k] = _TimedLogEntry(
            component, level, message, Timer(duration)
        )


def _format(x: Interpolation | str) -> str:
    return format(x.value, x.format_spec) if isinstance(x, Interpolation) else x


_instances: dict[str, Logger] = {}
_entries: list[_LogEntry] = []
_timed_entries: dict[_Key, _TimedLogEntry] = {}
