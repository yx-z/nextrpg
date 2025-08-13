from asyncio import sleep
from collections.abc import Callable
from dataclasses import KW_ONLY, replace

from nextrpg.core.dataclass_with_init import (
    dataclass_with_init,
    default,
    not_constructor_below,
)
from nextrpg.core.game_loop import GameLoop
from nextrpg.core.save import save_io
from nextrpg.global_config.global_config import Config, set_config
from nextrpg.scene.scene import Scene


@dataclass_with_init(frozen=True)
class Game:
    entry_scene: Callable[[], Scene]
    config: Config = Config()
    _: KW_ONLY = not_constructor_below()
    _loop: GameLoop = default(lambda self: GameLoop(self.entry_scene))

    def start(self) -> None:
        self._init()
        while self._loop.running:
            self._tick()

    async def start_web(self) -> None:
        self._init()
        while self._loop.running:
            self._tick()
            await sleep(0)

    def _init(self) -> None:
        cfg = self.config
        gui = save_io().load(cfg.gui)
        loaded = replace(cfg, gui=gui)
        set_config(loaded)

    def _tick(self) -> None:
        object.__setattr__(self, "_loop", self._loop.tick)
