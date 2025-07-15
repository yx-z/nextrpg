"""
Logging system for NextRPG games.

This module provides an on-screen logging system designed specifically
for NextRPG games. It supports different log levels, timed messages,
and component-based logging for better organization.

The logging system includes:
- Component-based loggers for different game systems
- Multiple log levels (DEBUG, INFO, WARNING, ERROR)
- Timed log messages that automatically disappear
- Template-based message formatting
- Configurable log duration and level filtering

The logger is designed to work seamlessly with the game loop and
provides both immediate and timed log message display.

Example:
    ```python
    from nextrpg.logger import Logger

    # Create a logger for a specific component
    logger = Logger("Player")

    # Log different types of messages
    logger.debug("Player moved to position (100, 200)")
    logger.info("Player collected item: Sword")
    logger.warning("Player health is low: 20%")
    logger.error("Failed to load save file")
    ```
"""

from dataclasses import dataclass, replace
from functools import cached_property
from string.templatelib import Interpolation, Template
from typing import NamedTuple

from nextrpg.global_config import config
from nextrpg.debug_config import LogLevel
from nextrpg.core import Millisecond, Timer


class DurationFromConfig:
    """
    Sentinel class to indicate that the log duration is taken from config.

    This class is used as a sentinel value to indicate that the log
    message duration should be taken from the global configuration
    rather than being specified explicitly.
    """


FROM_CONFIG = DurationFromConfig()
"""Sentinel object to indicate that the log duration is taken from config."""


@dataclass(frozen=True)
class Logger:
    """
    On-screen logger for NextRPG components.

    This class provides logging functionality for specific game components.
    Each logger instance is tied to a unique component name, allowing
    for organized and filtered logging output.

    The logger supports multiple log levels and can display messages
    either immediately or with a configurable duration.

    Arguments:
        `component`: Unique name of the component that the logger is for.
            This name is used to identify the source of log messages
            and can be used for filtering.

    Example:
        ```python
        from nextrpg.logger import Logger

        # Create loggers for different components
        player_logger = Logger("Player")
        enemy_logger = Logger("Enemy")

        # Use the loggers
        player_logger.info("Player moved")
        enemy_logger.warning("Enemy spotted player")
        ```
    """

    component: str

    def debug(
        self,
        message: Template | str,
        *,
        duration: Millisecond | DurationFromConfig | None = FROM_CONFIG,
    ) -> None:
        """
        Log a debug message.

        Debug messages are typically used for detailed information
        useful for debugging and development. They are usually only
        displayed when debug logging is enabled.

        Arguments:
            `message`: The message to log. Can be a string or template.

            `duration`: The duration of the log message in milliseconds.
                If `None`, the message will be flushed in the next game loop.
                If `FROM_CONFIG`, the duration is taken from
                `config().debug.log_duration`.

        Returns:
            `None`

        Example:
            ```python
            logger.debug("Player position: (100, 200)")
            logger.debug("Animation frame: 3/8", duration=2000)
            ```
        """
        _add(self.component, LogLevel.DEBUG, message, duration)

    def info(
        self,
        message: Template | str,
        *,
        duration: Millisecond | DurationFromConfig | None = None,
    ) -> None:
        """
        Log an info message.

        Info messages provide general information about game events
        and are typically displayed to provide context to the player.

        Arguments:
            `message`: The message to log. Can be a string or template.

            `duration`: The duration of the log message in milliseconds.
                If `None`, the message will be flushed in the next game loop.

        Returns:
            `None`

        Example:
            ```python
            logger.info("Welcome to the game!")
            logger.info("You found a treasure chest", duration=3000)
            ```
        """
        _add(self.component, LogLevel.INFO, message, duration)

    def warning(
        self,
        message: Template | str,
        *,
        duration: Millisecond | DurationFromConfig | None = None,
    ) -> None:
        """
        Log a warning message.

        Warning messages indicate potential issues or important
        information that the player should be aware of.

        Arguments:
            `message`: The message to log. Can be a string or template.

            `duration`: The duration of the log message in milliseconds.
                If `None`, the message will be flushed in the next game loop.

        Returns:
            `None`

        Example:
            ```python
            logger.warning("Your health is low!")
            logger.warning("Enemy approaching", duration=5000)
            ```
        """
        _add(self.component, LogLevel.WARNING, message, duration)

    def error(
        self,
        message: Template | str,
        *,
        duration: Millisecond | DurationFromConfig | None = None,
    ) -> None:
        """
        Log an error message.

        Error messages indicate serious problems or failures that
        need immediate attention.

        Arguments:
            `message`: The message to log. Can be a string or template.

            `duration`: The duration of the log message in milliseconds.
                If `None`, the message will be flushed in the next game loop.

        Returns:
            `None`

        Example:
            ```python
            logger.error("Failed to load save file")
            logger.error("Connection lost", duration=10000)
            ```
        """
        _add(self.component, LogLevel.ERROR, message, duration)

    def __new__(cls, component: str) -> Logger:
        """
        Create a new logger instance with component name validation.

        Ensures that each component name is unique across all logger
        instances to prevent confusion in log output.

        Arguments:
            `component`: The component name for the logger.

        Returns:
            `Logger`: A new logger instance.

        Raises:
            `ValueError`: If a logger with the same component name
                already exists.
        """
        if component in _instances:
            raise ValueError(
                f"Logger {component=} already exists."
                f"Use another name for better log separation."
            )

        _instances.add(component)
        return super().__new__(cls)


class ComponentAndMessage(NamedTuple):
    """
    Log component and message pair for formatted output.

    This named tuple represents a log message with its associated
    component name, used for displaying formatted log messages.

    Arguments:
        `component`: The name of the component that generated the log.

        `message`: The formatted log message text.
    """

    component: str
    message: str


def pop_messages(time_delta: Millisecond) -> tuple[ComponentAndMessage, ...]:
    """
    Pop all log messages and return them in a formatted fashion.

    This function retrieves all current log messages that meet the
    configured log level criteria and advances the timers for timed
    messages.

    Arguments:
        `time_delta`: Milliseconds since the last game loop.

    Returns:
        `tuple[ComponentAndMessage, ...]`: Tuple of log messages with
            their component names.

    Example:
        ```python
        # In the game loop
        messages = pop_messages(time_delta)
        for component, message in messages:
            display_log_message(component, message)
        ```
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
    """
    Internal key for timed log entries.

    Used internally to identify and manage timed log messages.

    Arguments:
        `component`: The component name.

        `template`: The message template as a tuple of strings.
    """

    component: str
    template: tuple[str, ...]


@dataclass(frozen=True)
class _LogEntry:
    """
    Internal representation of a log entry.

    Arguments:
        `component`: The component that generated the log.

        `level`: The log level of the message.

        `message`: The message template.
    """

    component: str
    level: LogLevel
    message: Template

    @cached_property
    def formatted(self) -> str:
        """
        Get the formatted message text.

        Returns:
            `str`: The formatted log message.
        """
        return "".join(_format(m) for m in self.message)


@dataclass(frozen=True)
class _TimedLogEntry(_LogEntry):
    """
    Internal representation of a timed log entry.

    Extends `_LogEntry` with timer functionality for messages
    that should disappear after a certain duration.

    Arguments:
        `timer`: The timer controlling the message duration.
    """

    timer: Timer


def _pop(time_delta: Millisecond) -> None:
    """
    Pop all log entries and update timed entries.

    Clears immediate log entries and advances timers for timed
    entries, removing those that have completed.

    Arguments:
        `time_delta`: Milliseconds since the last game loop.
    """
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
    duration: Millisecond | DurationFromConfig | None,
) -> None:
    """
    Add a log entry to the internal log system.

    This function handles the internal logic for adding log messages
    to the appropriate storage (immediate or timed) based on the
    duration parameter.

    Arguments:
        `component`: The component name.

        `level`: The log level.

        `message`: The message to log.

        `duration`: The duration for timed messages, or None for immediate.
    """
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


def _format(s: Interpolation | str) -> str:
    if isinstance(s, Interpolation):
        return format(s.value, s.format_spec)
    return s


_instances: set[str] = set()
_entries: list[_LogEntry] = []
_timed_entries: dict[_Key, _TimedLogEntry] = {}
