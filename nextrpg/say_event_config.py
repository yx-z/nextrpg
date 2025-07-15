"""
Say event configuration system for NextRPG.

This module provides configuration options for say events and
dialogue boxes in NextRPG games. It includes the `SayEventConfig`
class which defines visual and timing parameters for text display.

The say event configuration features:
- Background color and styling
- Border radius and padding settings
- Fade animation duration
- Text configuration integration

Example:
    ```python
    from nextrpg.say_event_config import SayEventConfig
    from nextrpg.core import Rgba, Pixel, Millisecond

    # Create default say event config
    config = SayEventConfig()

    # Create custom say event config
    custom_config = SayEventConfig(
        background=Rgba(0, 0, 0, 200),  # Semi-transparent black
        border_radius=Pixel(10),
        padding=Pixel(20),
        fade_duration=Millisecond(500)
    )
    ```
"""

from dataclasses import dataclass, replace
from functools import cached_property

from nextrpg.core import BLACK, WHITE, Millisecond, Pixel, Rgba
from nextrpg.model import export
from nextrpg.text_config import TextConfig


@export
@dataclass(frozen=True)
class SayEventConfig:
    """
    Configuration class for say events and dialogue boxes.

    This config defines the visual appearance and timing of
    dialogue boxes and text display events in NextRPG games.

    Arguments:
        `background`: The background color of the dialogue box.
            Defaults to white.

        `border_radius`: The border radius of the dialogue box
            in pixels. Defaults to 20 pixels.

        `padding`: The internal padding of the dialogue box
            in pixels. Defaults to 16 pixels.

        `fade_duration`: The duration of fade animations
            in milliseconds. Defaults to 200ms.

    Example:
        ```python
        from nextrpg.say_event_config import SayEventConfig
        from nextrpg.core import Rgba, Pixel, Millisecond

        # Default configuration
        config = SayEventConfig()

        # Dark theme configuration
        dark_config = SayEventConfig(
            background=Rgba(0, 0, 0, 200),
            border_radius=Pixel(10),
            padding=Pixel(20),
            fade_duration=Millisecond(300)
        )

        # Rounded configuration
        rounded_config = SayEventConfig(
            border_radius=Pixel(30),
            padding=Pixel(25)
        )
        ```
    """

    background: Rgba = WHITE
    border_radius: Pixel = 20
    padding: Pixel = 16
    fade_duration: Millisecond = 200

    @cached_property
    def text(self) -> TextConfig:
        """
        Get the text configuration for say events.

        Returns a text configuration with black color for
        good contrast against the white background.

        Returns:
            `TextConfig`: Text configuration with black color.

        Example:
            ```python
            # Get text config for say events
            text_config = say_event_config.text
            ```
        """
        from nextrpg.global_config import config

        return replace(config().text, color=BLACK)
