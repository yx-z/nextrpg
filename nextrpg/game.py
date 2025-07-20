"""
Main game loop and initialization for `nextrpg`.

This module provides the core game loop functionality and initialization for
`nextrpg` games. It handles the main game window setup, event processing, scene
management, and the primary game loop.

Features:
    - Main game controller (`Game`) for window and loop management
    - Internal game loop logic (`_GameLoop`)
    - Event processing and scene management
    - Synchronous and asynchronous game loop options
"""

from asyncio import sleep
from dataclasses import KW_ONLY
from typing import Callable

from nextrpg.core.game_loop import GameLoop
from nextrpg.core.model import (
    dataclass_with_instance_init,
    instance_init,
    not_constructor_below,
)
from nextrpg.scene.scene import Scene


@dataclass_with_instance_init
class Game:
    """
    Main game controller that sets up the game window and manages the game loop.

    This class is responsible for initializing the game window, loading
    the entry scene, and managing the overall game state. It provides
    both synchronous and asynchronous game loop options.

    Arguments:
        `entry_scene`: A function that returns the entry scene.
            This must be a function rather than a direct `Scene` instance
            because drawings can only be loaded after pygame initialization.

    Example:
        ```python
        from nextrpg.game import Game
        from nextrpg.scene import MapScene

        def create_scene():
            return MapScene("maps/town.tmx")

        game = Game(entry_scene=create_scene)
        game.start()
        ```
    """

    entry_scene: Callable[[], Scene]
    _: KW_ONLY = not_constructor_below()
    _loop: GameLoop = instance_init(
        lambda self: GameLoop(entry_scene=self.entry_scene)
    )

    def start(self) -> None:
        """
        Start the game in a local pygame window with synchronous game loop.

        This method runs the game loop synchronously, which is suitable
        for desktop applications. The game will run until the window is
        closed or the game loop is explicitly stopped.

        Example:
            ```python
            game = Game(entry_scene=create_scene)
            game.start()  # Blocks until game ends
            ```
        """
        while self._loop.running:
            self._tick()

    async def start_async(self) -> None:
        """
        Start the game in async fashion for web/pygbag compatibility.

        This method runs the game loop asynchronously, which is required
        for web deployment with pygbag. It yields control periodically
        to allow other async operations to run.

        Example:
            ```python
            game = Game(entry_scene=create_scene)
            await game.start_async()  # Non-blocking async loop
            ```
        """
        while self._loop.running:
            self._tick()
            await sleep(0)

    def _tick(self) -> None:
        """
        Execute one tick of the game loop.

        Updates the internal game loop state by calling the tick method
        on the current loop instance.
        """
        object.__setattr__(self, "_loop", self._loop.tick)
