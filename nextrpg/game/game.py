import logging
from asyncio import sleep
from collections.abc import Callable
from dataclasses import KW_ONLY

from pygame import font, init

from nextrpg.config.config import Config, set_config
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.game.game_loop import GameLoop
from nextrpg.scene.scene import Scene


@dataclass_with_default(frozen=True)
class Game:
    entry_scene: Callable[[], Scene]
    config: Config = Config()
    _: KW_ONLY = private_init_below()
    __: None = default(lambda self: self._init())
    _loop: GameLoop = default(lambda self: GameLoop(self.entry_scene))

    def start(self) -> None:
        while self._loop.running:
            self._tick()

    async def start_web(self) -> None:
        while self._loop.running:
            self._tick()
            await sleep(0)

    def _init(self) -> None:
        if debug := self.config.debug:
            logging.basicConfig(**debug.console_log_configs)
        init()
        font.init()
        set_config(self.config)

    def _tick(self) -> None:
        object.__setattr__(self, "_loop", self._loop.tick)
