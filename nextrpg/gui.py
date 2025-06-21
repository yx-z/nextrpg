"""
Game window / Graphical User Interface (GUI).
"""

from dataclasses import dataclass, field
from functools import cached_property

from pygame import Surface
from pygame.transform import smoothscale

from nextrpg.config import config
from nextrpg.core import Coordinate, Size
from nextrpg.draw_on_screen import DrawOnScreen, Drawing


@dataclass(frozen=True)
class Gui:
    """
    Initialize a `Gui` instance that scales and centers drawings.

    Args:
        `window`: Size of the window. If `None`, default to
            the GUI size from `config().gui`.
    """

    window: Size = field(default_factory=lambda: config().gui.size)

    @cached_property
    def _scale(self) -> float:
        return min(
            self.window.width / config().gui.size.width,
            self.window.height / config().gui.size.height,
        )

    @cached_property
    def _center_shift(self) -> Coordinate:
        return Coordinate(
            (self.window.width - self._scale * config().gui.size.width) / 2,
            (self.window.height - self._scale * config().gui.size.height) / 2,
        )

    def scale(self, draws: list[DrawOnScreen]) -> DrawOnScreen:
        """
        Scale and center all drawings to a single surface.

        This shall be the final step before rendering to the screen.
        All other in-game visual transformation logic shall assume using
        the native/unscaled screen size from `config().gui.size`.

        Args:
            `draws`: A list of drawings to be scaled and centered.

        Returns:
            `DrawOnScreen`: The scaled drawing that stacks all drawings.
        """
        screen = Surface(config().gui.size.tuple)
        screen.blits(d.pygame for d in draws)
        scaled_size = config().gui.size * self._scale
        return DrawOnScreen(
            self._center_shift, Drawing(smoothscale(screen, scaled_size.tuple))
        )
