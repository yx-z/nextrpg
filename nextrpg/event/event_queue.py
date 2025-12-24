from collections.abc import Callable, Iterable
from dataclasses import dataclass, replace
from typing import Self

import pygame

from nextrpg.core.time import Millisecond
from nextrpg.event.base_event import BaseEvent
from nextrpg.event.io_event import to_io_event
from nextrpg.event.user_event import NEXTRPG_USER_EVENT_ID
from nextrpg.game.game_state import GameState


@dataclass(frozen=True)
class EventQueue:
    events: tuple[_EventAndDelay, ...] = ()

    def __iter__(self) -> Iterable[BaseEvent]:
        for event in self.events:
            if not callable(event.delay) and event.delay <= 0:
                yield event.event

    def tick(self, time_delta: Millisecond, state: GameState) -> Self:
        events: list[_EventAndDelay] = []
        for pygame_event in pygame.event.get():
            if pygame_event.type != NEXTRPG_USER_EVENT_ID:
                event = to_io_event(pygame_event)
                delay = 0
            else:
                event = pygame_event.dict["user_event"]
                delay = pygame_event.dict["delay"]
            event_and_delay = _EventAndDelay(event, delay)
            events.append(event_and_delay)

        for event in self.events:
            if callable(predicate := event.delay):
                if predicate(state):
                    res = replace(event, delay=0)
                else:
                    res = event
            else:
                if event.delay <= 0:
                    continue
                delay = event.delay - time_delta
                res = replace(event, delay=delay)
            events.append(res)
        return replace(self, events=tuple(events))


@dataclass(frozen=True)
class _EventAndDelay:
    event: BaseEvent
    delay: Millisecond | Callable[[GameState], bool]
