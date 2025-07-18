"""
Static scene implementation for `NextRPG`.

This module provides a simple static scene implementation that displays either a
solid color background or a single drawing resource. It's useful for simple
scenes like title screens, loading screens, or background-only scenes.

The static scene features:
- Solid color background support
- Single drawing resource display
- Automatic screen filling for color backgrounds
- Integration with the transition system
"""

from dataclasses import dataclass, field
from functools import cached_property

from nextrpg.draw.color import Rgba
from nextrpg.draw.draw_on_screen import DrawOnScreen
from nextrpg.global_config.global_config import config
from nextrpg.gui.area import screen
from nextrpg.scene.transition_scene import TransitioningScene


@dataclass(frozen=True)
class StaticScene(TransitioningScene):
    """
    Static scene that displays a single resource or color background.

    This class provides a simple scene implementation that displays either a
    solid color background or a single drawing resource. It's designed for
    simple scenes that don't require complex rendering or interaction.

    Arguments:
        `resource`: The resource to display. Can be either a color for a solid
            background or a drawing for a single image. Defaults to the GUI
            background color.
    """

    resource: Rgba | DrawOnScreen | tuple[DrawOnScreen, ...] = field(
        default_factory=lambda: config().gui.background_color
    )

    @cached_property
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        """
        Get the drawings to render for this scene.

        If the resource is a color, returns a screen-filling rectangle with that
        color. If the resource is a drawing, returns the drawing as-is.

        Returns:
            `tuple[DrawOnScreen, ...]`: The drawings to render.
        """
        if isinstance(self.resource, Rgba):
            return (screen().fill(self.resource),)
        if isinstance(self.resource, DrawOnScreen):
            return (self.resource,)
        return self.resource
