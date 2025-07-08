from pytest_mock import MockerFixture

from nextrpg.draw_on_screen import DrawOnScreen, Drawing
from nextrpg.coordinate import Coordinate
from nextrpg.scene.scene import Scene
from nextrpg.scene.transition_scene import TransitionScene
from test.util import MockSurface


def test_transition_scene(mocker: MockerFixture) -> None:
    scene1 = Scene()
    scene2 = Scene()
    scene2.draw_on_screens = (
        DrawOnScreen(Coordinate(1, 2), Drawing(MockSurface())),
    )
    transition = TransitionScene(scene1, scene2)
    assert transition.tick(10000) is scene2
    mocker.patch("nextrpg.draw_on_screen.Drawing.set_alpha")
    assert transition.draw_on_screens
