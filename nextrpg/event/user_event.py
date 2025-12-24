import logging
from collections.abc import Callable, Iterable

import pygame
from pygame import Event

from nextrpg.core.logger import Logger
from nextrpg.core.time import Millisecond
from nextrpg.core.util import type_name
from nextrpg.event.base_event import BaseEvent
from nextrpg.game.game_state import GameState

console_logger = logging.getLogger("user_event")
on_screen_logger = Logger("user_event")


class UserEvent(BaseEvent):
    def post(
        self, delay: Millisecond | Callable[[GameState], bool] = 0
    ) -> None:
        on_screen_logger.debug(f"Posting {delay=} {type_name(self)}")
        console_logger.debug(f"Posting {delay=} {self=}")
        pygame_event = Event(
            NEXTRPG_USER_EVENT_ID, user_event=self, delay=delay
        )
        pygame.event.post(pygame_event)


NEXTRPG_USER_EVENT_ID = pygame.event.custom_type()


def post_user_event(
    *event: UserEvent | Iterable[UserEvent],
    delay: Millisecond | Callable[[GameState], bool] = 0,
) -> None:
    if isinstance(event, UserEvent):
        event.post(delay)
    for ev in event:
        if isinstance(ev, UserEvent):
            ev.post(delay)
            continue
        for e in ev:
            e.post(delay)
