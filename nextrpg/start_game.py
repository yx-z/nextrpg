from dataclasses import astuple
from typing import Callable

from pygame import QUIT, VIDEORESIZE, event, init, transform
from pygame.constants import RESIZABLE
from pygame.display import flip, set_caption, set_mode
from pygame.time import Clock

from nextrpg.common_types import Millesecond
from nextrpg.config import GuiConfig
from nextrpg.drawable import Drawable
from nextrpg.scene import Scene


def start_game(config: GuiConfig,
                     entry_scene: Callable[[], Scene]) -> None:
    init()
    set_caption(config.title)
    screen = set_mode(
        astuple(config.size), RESIZABLE if config.allow_resize else 0
    )
    scene = entry_scene()
    clock = Clock()
    scale = 1.0
    while True:
        for e in event.get():
            scene.event(event=e)
            if e.type == QUIT:
                return
            if e.type == VIDEORESIZE:
                scale = min(e.w / config.size.width, e.h / config.size.height)

        screen.blits(
            Drawable(
                transform.scale(
                    drawable.surface, astuple(drawable.size * scale)
                ),
                drawable.coordinate * scale,
            ).pygame
            for drawable in scene.draw(Millesecond(clock.get_time()))
        )
        flip()
        clock.tick(config.frames_per_second)
