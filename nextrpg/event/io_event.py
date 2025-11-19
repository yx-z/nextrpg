from dataclasses import dataclass
from functools import cached_property
from typing import Any, TypeIs

import pygame
from pygame import KEYDOWN, KEYUP, MOUSEBUTTONDOWN, QUIT, VIDEORESIZE, Event

from nextrpg.config.system.key_mapping_config import KeyCode, KeyMapping
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size


@dataclass(frozen=True)
class IoEvent:
    event: Event


class Quit(IoEvent):
    pass


class WindowResize(IoEvent):
    @cached_property
    def size(self) -> Size:
        return Size(self.event.w, self.event.h)


def is_key_press(
    event: IoEvent, key: KeyMapping | KeyCode | None
) -> TypeIs[KeyPressDown]:
    if isinstance(key, KeyMapping):
        key_code = key.resolve
    else:
        key_code = key
    return isinstance(event, KeyPressDown) and event.key == key_code


class _KeyPressEvent(IoEvent):
    @cached_property
    def key(self) -> KeyCode:
        return self.event.key

    @cached_property
    def key_mapping(self) -> KeyMapping | None:
        return KeyMapping.from_key(self.key)


class KeyPressDown(_KeyPressEvent):
    pass


class KeyPressUp(_KeyPressEvent):
    pass


class _MouseButtonEvent(IoEvent):
    @cached_property
    def coordinate(self) -> Coordinate:
        return Coordinate(*self.event.pos)


class MouseButtonDown(_MouseButtonEvent):
    pass


class MouseButtonUp(_MouseButtonEvent):
    pass


def to_io_event(event: Event) -> IoEvent:
    return {
        QUIT: Quit,
        VIDEORESIZE: WindowResize,
        KEYDOWN: KeyPressDown,
        KEYUP: KeyPressUp,
        MOUSEBUTTONDOWN: MouseButtonDown,
    }.get(event.type, IoEvent)(event)


def quit(*args: Any, **kwargs: Any) -> None:
    event_quit = Event(QUIT)
    pygame.event.post(event_quit)
