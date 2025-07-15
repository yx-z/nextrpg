"""
Main game loop and initialization for NextRPG.

This module provides the core game loop functionality and initialization
for NextRPG games. It handles the main game window setup, event
processing, scene management, and the primary game loop.

The module contains two main classes:
- `Game`: The main game controller that manages the game window and loop
- `_GameLoop`: Internal class that handles the actual game loop logic

The game loop processes events, updates scenes, and manages the GUI
components while maintaining a consistent frame rate.

Example:
    ```python
    from nextrpg.game import Game
    from nextrpg.scene import StaticScene

    def create_entry_scene():
        return StaticScene()

    game = Game(entry_scene=create_entry_scene)
    game.start()  # Synchronous game loop
    # or
    await game.start_async()  # Asynchronous game loop
    ```
"""

from asyncio import sleep
from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from types import ModuleType
from typing import Callable, Self

import pygame
from pygame.time import Clock

from nextrpg.global_config import config
from nextrpg import plugins
from nextrpg.pygame_event import PygameEvent, Quit, to_typed_event
from nextrpg.gui import Gui
from nextrpg.logger import Logger
from nextrpg.model import (
    dataclass_with_instance_init,
    export,
    instance_init,
    not_constructor_below,
)
from nextrpg.scene import Scene

logger = Logger("Game")


@export
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
    event_modules: tuple[ModuleType] = (plugins,)
    _: KW_ONLY = not_constructor_below()
    _loop: _GameLoop = instance_init(
        lambda self: _GameLoop(entry_scene=self.entry_scene)
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


@dataclass_with_instance_init
class _GameLoop:
    """
    Internal game loop implementation.

    This class handles the core game loop logic including event processing,
    scene updates, GUI management, and frame rate control. It's designed
    to be used internally by the `Game` class.

    Arguments:
        `entry_scene`: Function that creates the initial scene.

        `running`: Whether the game loop should continue running.

        `_clock`: Pygame clock for frame rate control.

        `_gui`: GUI manager for window and drawing operations.

        `_scene`: Current active scene being rendered and updated.
    """

    entry_scene: Callable[[], Scene]
    _: KW_ONLY = not_constructor_below()
    running: bool = True
    _clock: Clock = field(default_factory=Clock)
    _gui: Gui = field(default_factory=Gui)
    _scene: Scene = instance_init(lambda self: self.entry_scene())

    @cached_property
    def tick(self) -> Self:
        """
        Execute one tick of the game loop.

        This method processes the game loop for one frame, including:
        - Frame rate control and timing
        - Scene drawing and updates
        - GUI updates
        - Event processing

        Returns:
            `_GameLoop`: Updated game loop state.

        Example:
            ```python
            loop = _GameLoop(entry_scene=create_scene)
            loop = loop.tick()  # Process one frame
            ```
        """
        logger.debug(t"FPS: {self._clock.get_fps():.0f}", duration=None)
        self._clock.tick(config().gui.frames_per_second)
        time_delta = self._clock.get_time()

        gui = self._gui.update
        gui.draw(self._scene.draw_on_screens, time_delta)

        loop = replace(self, _scene=self._scene.tick(time_delta), _gui=gui)
        for e in pygame.event.get():
            loop = loop._event(to_typed_event(e))
        return loop

    def _event(self, e: PygameEvent) -> Self:
        """
        Process a single pygame event.

        Handles the event by passing it to both the current scene and
        GUI components. Updates the running state if a quit event is
        received.

        Arguments:
            `e`: The pygame event to process.

        Returns:
            `_GameLoop`: Updated game loop state after event processing.
        """
        return replace(
            self,
            _scene=self._scene.event(e),
            _gui=self._gui.event(e),
            running=not isinstance(e, Quit),
        )
