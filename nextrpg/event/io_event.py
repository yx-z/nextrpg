from collections.abc import Iterable
from dataclasses import dataclass, fields
from functools import cached_property
from typing import Any, TypeIs

import pygame
from pygame import KEYDOWN, KEYUP, MOUSEBUTTONDOWN, QUIT, VIDEORESIZE, Event

from nextrpg.config.config import config
from nextrpg.config.system.key_mapping_config import KeyCode, KeyMapping
from nextrpg.event.base_event import BaseEvent
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.size import Size


@dataclass(frozen=True)
class IoEvent(BaseEvent):
    event: Event


class Quit(IoEvent):
    pass


class WindowResize(IoEvent):
    @cached_property
    def size(self) -> Size:
        return Size(self.event.w, self.event.h)


def is_key_press(
    event: BaseEvent, key: KeyMapping | KeyCode | tuple[KeyCode, ...]
) -> TypeIs[KeyPressDown]:
    if not isinstance(event, KeyPressDown):
        return False
    if isinstance(key, int):
        return event.key == key
    key_mappings = config().system.key_mapping
    key_mapping = getattr(key_mappings, key.name)
    return (
        event.key == key_mapping
        or isinstance(key_mapping, Iterable)
        and event.key in key_mapping
    )


class _KeyPressEvent(IoEvent):
    @cached_property
    def key(self) -> KeyCode:
        return self.event.key

    @cached_property
    def key_mapping(self) -> KeyMapping | None:
        key_mappings = config().system.key_mapping
        for field in fields(key_mappings):
            key_codes = getattr(key_mappings, field.name)
            if self.key == key_codes or (
                isinstance(key_codes, Iterable) and self.key in key_codes
            ):
                return KeyMapping(field.name)
        return None


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
    return _event_types.get(event.type, IoEvent)(event)


_event_types = {
    QUIT: Quit,
    VIDEORESIZE: WindowResize,
    KEYDOWN: KeyPressDown,
    KEYUP: KeyPressUp,
    MOUSEBUTTONDOWN: MouseButtonDown,
}


def post_quit_event(*args: Any, **kwargs: Any) -> None:
    event_quit = Event(QUIT)
    pygame.event.post(event_quit)
