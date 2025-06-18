"""
Game window / Graphical User Interface (GUI).
"""

from typing import Final

from pygame import Surface
from pygame.transform import smoothscale

from nextrpg.config import config
from nextrpg.core import Coordinate, Pixel, Size
from nextrpg.draw_on_screen import DrawOnScreen


class Gui:
    """
    Handles scaling and centering of drawings for the game window.
    """

    def __init__(self, window: Size | None = None) -> None:
        """
        Initialize a `Gui` instance.

        Args:
            `window`: Size of the window. If `None`, default to
                the GUI size from `config().gui`.
        """
        window = window or config().gui.size
        self._scale: Final[float] = min(
            window.width / (width := config().gui.size.width),
            window.height / (height := config().gui.size.height),
        )
        self._center_shift: Final[Coordinate] = Coordinate(
            (window.width - self._scale * width) / 2,
            (window.height - self._scale * height) / 2,
        )

    def scale(
        self, draws: list[DrawOnScreen]
    ) -> tuple[Surface, tuple[Pixel, Pixel]]:
        """
        Sale and center the given drawings for the game window.

        Args:
            `draws`: A list of draws to be scaled and centered.

        Returns:
            `tuple[Surface, tuple[Pixel, Pixel]]`: scaled and centered screen.
        """
        screen = Surface(config().gui.size.tuple)
        screen.blits(d.pygame for d in draws)
        return (
            smoothscale(screen, (config().gui.size * self._scale).tuple),
            self._center_shift.tuple,
        )
