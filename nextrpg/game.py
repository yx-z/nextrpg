from asyncio import sleep
from collections.abc import Callable
from dataclasses import KW_ONLY

from nextrpg.core.dataclass_with_init import (
    dataclass_with_init,
    default,
    not_constructor_below,
)
from nextrpg.core.game_loop import GameLoop
from nextrpg.scene.scene import Scene


@dataclass_with_init(frozen=True)
class Game:
    entry_scene: Callable[[], Scene]
    _: KW_ONLY = not_constructor_below()
    _loop: GameLoop = default(lambda self: GameLoop(self.entry_scene))

    def start(self) -> None:
        while self._loop.running:
            self._tick()

    async def start_web(self) -> None:
        while self._loop.running:
            self._tick()
            await sleep(0)

    def _tick(self) -> None:
        object.__setattr__(self, "_loop", self._loop.tick)
