from collections import namedtuple
from dataclasses import dataclass, field
from functools import cached_property
from string.templatelib import Interpolation, Template


class LogEntry(namedtuple("LogEntry", "component log")):
    component: str
    log: Template

    @cached_property
    def formatted_log(self) -> str:
        return "".join(map(_format, self.log))


def _format(x: Interpolation | str) -> str:
    return format(x.value, x.format_spec) if isinstance(x, Interpolation) else x


@dataclass
class LogEntries:
    entries: list[LogEntry] = field(default_factory=list)

    def append(self, entry: LogEntry) -> None:
        self.entries.append(entry)

    def clear(self) -> None:
        self.entries.clear()

    @property
    def formatted_log(self) -> list[str]:
        if not self.entries:
            return []
        max_len = max(len(e.component) for e in self.entries)
        return [
            f"{e.component.ljust(max_len)} | {e.formatted_log}"
            for e in self.entries
        ]


_debug_logs = LogEntries()


def debug_log(component: str, log: Template) -> None:
    """
    Put a line of debug log on the screen.

    Arguments:
        `component`: The current component trying to log.

        `log`: str to print on screen.

    Returns:
        `None`.
    """
    _debug_logs.append(LogEntry(component, log))


def get_debug_logs() -> LogEntries:
    """
    Get current debug logs that aren't printed.

    Returns:
        `LogEntries`: Log entries of all debug logs in the current iteration.
    """
    return _debug_logs


def clear_debug_logs() -> None:
    """
    Clear debug logs.

    Returns:
        `None`.
    """
    _debug_logs.clear()
