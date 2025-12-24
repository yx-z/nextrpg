import logging
from dataclasses import dataclass
from enum import IntEnum, auto
from functools import cached_property
from typing import Any

from frozendict import frozendict

from nextrpg.config.drawing.text_config import TextConfig
from nextrpg.core.time import Millisecond
from nextrpg.drawing.color import Color

type LOG_LEVEL = int


class LogLevel(IntEnum):
    DEBUG = auto()
    INFO = auto()
    ERROR = auto()

    @cached_property
    def stdlib(self) -> LOG_LEVEL:
        return _LOG_LEVEL[self]


@dataclass(frozen=True)
class LoggingConfig:
    background_color: Color | None = Color(0, 0, 0, 64)
    level: LogLevel = LogLevel.DEBUG
    exclude_on_screen_loggers: tuple[str, ...] = ()
    default_on_screen_duration: Millisecond = 2000
    console_logger_kwargs: frozendict[str, Any] = frozendict()
    text_config_input: TextConfig | None = None

    @cached_property
    def text(self) -> TextConfig:
        from nextrpg.config.config import config

        if self.text_config_input:
            return self.text_config_input
        return config().drawing.text


_LOG_LEVEL = {
    LogLevel.DEBUG: logging.DEBUG,
    LogLevel.INFO: logging.INFO,
    LogLevel.ERROR: logging.ERROR,
}
