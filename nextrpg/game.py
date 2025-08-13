from asyncio import sleep
from collections.abc import Callable
from dataclasses import KW_ONLY, field, replace

from nextrpg.core.dataclass_with_init import (
    dataclass_with_init,
    default,
    not_constructor_below,
)
from nextrpg.core.game_loop import GameLoop
from nextrpg.core.save import save_io
from nextrpg.global_config.global_config import Config, config, set_config
from nextrpg.global_config.gui_config import GuiConfig
from nextrpg.scene.scene import Scene


@dataclass_with_init(frozen=True)
class Game:
    entry_scene: Callable[[], Scene]
    config: Config = field(default_factory=lambda: config())
    _: KW_ONLY = not_constructor_below()
    _loop: GameLoop = default(lambda self: GameLoop(self.entry_scene))
    __: None = default(lambda self: self._init())

    def start(self) -> None:
        while self._loop.running:
            self._tick()

    async def start_web(self) -> None:
        while self._loop.running:
            self._tick()
            await sleep(0)

    def _init(self) -> None:
        if gui := save_io().load(GuiConfig):
            set_config(replace(self.config, gui=gui))
        else:
            set_config(self.config)

    def _tick(self) -> None:
        object.__setattr__(self, "_loop", self._loop.tick)
