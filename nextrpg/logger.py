"""
Logger module.
"""

from dataclasses import dataclass, replace
from functools import cached_property
from string.templatelib import Interpolation, Template
from typing import NamedTuple

from nextrpg.config import LogLevel, config
from nextrpg.core import Millisecond, Timer


class DurationFromConfig:
    """
    Sentinel class to indicate that the log duration is taken from config.
    """


FROM_CONFIG = DurationFromConfig()
"""Sentinel object to indicate that the log duration is taken from config."""


@dataclass(frozen=True)
class Logger:
    """
    On-screen logger.

    Arguments:
        `component`: Unique name of the component that the logger is for.
    """

    component: str

    def debug(
        self,
        message: Template | str,
        *,
        duration: Millisecond | DurationFromConfig | None = None,
    ) -> None:
        """
        Debug log message.

        Arguments:
            `message`: The message to log.

            `duration`: The duration of the log message. If `None`, the message
                will be flushed in next game loop. If `FROM_CONFIG`, the
                duration is taken from `config().debug.log_duration`.

        Returns:
            `None`
        """
        _add(self.component, LogLevel.DEBUG, message, duration)

    def info(
        self,
        message: Template | str,
        *,
        duration: Millisecond | DurationFromConfig | None = None,
    ) -> None:
        """
        Info log message.

        Arguments:
            `message`: The message to log.

            `duration`: The duration of the log message.

        Returns:
            `None`
        """
        _add(self.component, LogLevel.INFO, message, duration)

    def warning(
        self,
        message: Template | str,
        *,
        duration: Millisecond | DurationFromConfig | None = None,
    ) -> None:
        """
        Warning log message.

        Arguments:
            `message`: The message to log.

            `duration`: The duration of the log message.

        Returns:
            `None`
        """
        _add(self.component, LogLevel.WARNING, message, duration)

    def error(
        self,
        message: Template | str,
        *,
        duration: Millisecond | DurationFromConfig | None = None,
    ) -> None:
        """
        Error log message.

        Arguments:
            `message`: The message to log.

            `duration`: The duration of the log message.

        Returns:
            `None`
        """
        _add(self.component, LogLevel.ERROR, message, duration)

    def __new__(cls, component: str) -> Logger:
        if component in _instances:
            raise ValueError(
                f"Logger {component=} already exists."
                f"Use another name for better log separation."
            )

        _instances.add(component)
        return super().__new__(cls)


class ComponentAndMessage(NamedTuple):
    """
    Log component and message pair.
    """

    component: str
    message: str


def pop_messages(time_delta: Millisecond) -> tuple[ComponentAndMessage, ...]:
    """
    Pop all log messages and return them in a formatted fashion.

    Arguments:
        `time_delta`: Milliseconds since the last game loop.

    Returns:
        `tuple[ComponentAndMessage]`: Tuple of log messages.
    """
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

    @cached_property
    def formatted(self) -> str:
        return "".join(map(_format, self.message))


@dataclass(frozen=True)
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
    message: Template | str,
    duration: Millisecond | DurationFromConfig | None,
) -> None:
    if not (debug := config().debug):
        return
    message = Template(message) if isinstance(message, str) else message
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


_instances: set[str] = set()
_entries: list[_LogEntry] = []
_timed_entries: dict[_Key, _TimedLogEntry] = {}
