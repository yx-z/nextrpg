from nextrpg.draw.coordinate import Coordinate
from nextrpg.draw.draw_on_screen import DrawOnScreen, Drawing
from nextrpg.scene.static_scene import StaticScene
from test.util import MockSurface


def test_static_scene() -> None:
    assert StaticScene().draw_on_screens
    assert StaticScene(
        DrawOnScreen(Coordinate(0, 0), Drawing(MockSurface()))
    ).draw_on_screens
