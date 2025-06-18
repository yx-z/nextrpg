"""
Start the game window and game loop.
"""

from asyncio import run, sleep
from dataclasses import dataclass
from typing import Callable

import pygame
from pygame import Surface, init
from pygame.display import flip, set_caption, set_mode
from pygame.locals import RESIZABLE
from pygame.time import Clock

from nextrpg.config import config
from nextrpg.event.pygame_event import (
    GuiResize,
    PygameEvent,
    Quit,
    to_typed_event,
)
from nextrpg.scene.scene import Scene


@dataclass
class Game:
    _screen: Surface
    _scene: Scene
    _clock: Clock
    _scale: float

    @classmethod
    def load(
        cls,
        entry_scene: Callable[[], Scene],
        clock: Clock = Clock(),
        scale: float = 1.0,
    ) -> "Game":
        return Game(_init_screen(), entry_scene(), clock, scale)

    def start(self) -> None:
        run(self.start_web())

    async def start_web(self) -> None:
        while True:
            if await self._loop():
                return

    async def _loop(self) -> bool:
        if any(self._event(to_typed_event(e)) for e in pygame.event.get()):
            return True
        self._step()
        await sleep(0)
        return False

    def _event(self, event: PygameEvent) -> bool:
        self._scene = self._scene.event(event)
        match event:
            case Quit():
                return True
            case GuiResize() as g:
                self._scale = min(
                    g.size.width / config().gui.size.width,
                    g.size.height / config().gui.size.height,
                )
        return False

    def _step(self) -> None:
        self._scene = self._scene.step(self._clock.get_time())
        self._screen.fill(config().gui.background_color.tuple)
        self._screen.blits(
            (d * self._scale).pygame for d in self._scene.draw_on_screen
        )
        flip()
        self._clock.tick(config().gui.frames_per_second)
        print(self._clock)


def _init_screen() -> Surface:
    init()
    set_caption(config().gui.title)
    return set_mode(
        config().gui.size.tuple, RESIZABLE if config().gui.resize else 0
    )
