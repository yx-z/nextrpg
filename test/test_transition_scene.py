from nextrpg.draw_on_screen import Coordinate, DrawOnScreen, Drawing
from nextrpg.scene.scene import Scene
from nextrpg.scene.transition_scene import TransitionScene
from test.util import MockSurface


def test_transition_scene() -> None:
    scene1 = Scene()
    scene2 = Scene()
    scene2.draw_on_screens = [
        DrawOnScreen(Coordinate(1, 2), Drawing(MockSurface()))
    ]
    transition = TransitionScene(scene1, scene2)
    assert transition.draw_on_screens is scene2.draw_on_screens
    assert transition.step(10) is scene2
