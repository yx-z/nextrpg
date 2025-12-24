from asyncio import sleep
from collections.abc import Callable
from dataclasses import KW_ONLY

import pygame

from nextrpg.config.config import Config, set_config
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.game.game_loop import GameLoop
from nextrpg.game.game_state import GameState
from nextrpg.scene.scene import Scene


@dataclass_with_default(frozen=True)
class Game:
    entry_scene: Callable[[], Scene]
    state: GameState = GameState()
    config: Config = Config()
    _: KW_ONLY = private_init_below()
    __: None = default(lambda self: self._init)
    _loop: GameLoop = default(
        lambda self: GameLoop(self.entry_scene, self.state)
    )

    def start(self) -> None:
        while self._loop.running:
            self._tick()

    async def start_web(self) -> None:
        while self._loop.running:
            self._tick()
            await sleep(0)

    @property
    def _init(self) -> None:
        pygame.init()
        set_config(self.config)

    def _tick(self) -> None:
        object.__setattr__(self, "_loop", self._loop.tick)
