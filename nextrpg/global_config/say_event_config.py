"""
Say event configuration system for `NextRPG`.

This module provides configuration options for say events and dialogue boxes in
`NextRPG` games. It includes the `SayEventConfig` class which defines visual
and timing parameters for text display.

The say event configuration features:
- Background color and styling
- Border radius and padding settings
- Fade animation duration
- Text configuration integration
"""

from dataclasses import dataclass

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Pixel
from nextrpg.core.time import Millisecond
from nextrpg.draw.color import Rgba, WHITE
from nextrpg.global_config.text_config import TextConfig


@dataclass(frozen=True)
class SayEventConfig:
    """
    Configuration class for say events and dialogue boxes.

    This global_config defines the visual appearance and timing of dialogue boxes and
    text display events in `NextRPG` games.

    Arguments:
        `background`: The background color of the dialogue box. Defaults to
            white.
        `border_radius`: The border radius of the dialogue box in pixels.
            Defaults to 20 pixels.
        `padding`: The internal padding of the dialogue box in pixels. Defaults
            to 16 pixels.
        `fade_duration`: The duration of fade animations in milliseconds.
            Defaults to 200ms.
    """

    background: Rgba = WHITE
    border_radius: Pixel = 16
    padding: Pixel = 16
    fade_duration: Millisecond = 200
    text_delay: Millisecond | None = 20
    name_color: Rgba | None = None
    center: Coordinate | None = None
    text: TextConfig | None = None
    drawing: "Drawing | None" = None
