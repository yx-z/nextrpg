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

from dataclasses import dataclass, replace

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Pixel, Size
from nextrpg.core.time import Millisecond
from nextrpg.draw.color import BLACK, WHITE, Rgba
from nextrpg.global_config.text_config import TextConfig


@dataclass(frozen=True)
class AddOnConfig:
    add_on_shift: Size = Size(0, 100)
    tail_base1_shift: Pixel = 10
    tail_base2_shift: Pixel = 30
    tail_tip_shift: Size = Size(0, 0)


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
    fade_duration: Millisecond = 200
    padding: Pixel = 16
    text_delay: Millisecond = 20
    name_color: Rgba = Rgba(0, 0, 255, 255)
    add_on: AddOnConfig = AddOnConfig()
    name_override: str | None = None
    coordinate: Coordinate | None = None
    avatar: "Draw | Group | None" = None
    text: TextConfig | None = None

    @property
    def default_text_config(self) -> TextConfig:
        from nextrpg.global_config.global_config import config

        return replace(config().text, color=BLACK)

    @property
    def default_scene_coordinate(self) -> Coordinate:
        from nextrpg.gui.area import screen

        return screen().center
