from functools import cached_property

from nextrpg.core import Millisecond
from nextrpg.draw_on_screen import DrawOnScreen
from nextrpg.model import Model
from nextrpg.scene.scene import Scene


class TransitionScene(Model, Scene):
    """
    Transition from one scene to another.

    Attributes:
        `from_scene`: The scene to transition from.

        `to_scene`: The scene to transition to.
    """

    from_scene: Scene
    to_scene: Scene

    @cached_property
    def draw_on_screens(self) -> list[DrawOnScreen]:
        return self.to_scene.draw_on_screens

    def step(self, time_delta: Millisecond) -> Scene:
        return self.to_scene
