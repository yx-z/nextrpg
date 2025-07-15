from dataclasses import dataclass

from nextrpg.core import Font, Pixel, Rgba, WHITE
from nextrpg.model import export


@export
@dataclass(frozen=True)
class TextConfig:
    """
    Configuration class for text rendering.

    Arguments:
        `font`: The font to use for rendering text.

        `color`: The color to use for rendering text.

        `line_spacing`: The line spacing to use for rendering text.

        `antialias`: Whether to use antialiasing for rendering text.
    """

    font: Font = Font(28)
    color: Rgba = WHITE
    line_spacing: Pixel = 8
    antialias: bool = True
