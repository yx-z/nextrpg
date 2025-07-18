from test.util import MockSurface

from nextrpg import Coordinate, Drawing, DrawOnScreen, StaticScene


def test_static_scene() -> None:
    assert StaticScene().draw_on_screens
    assert StaticScene(
        DrawOnScreen(Coordinate(0, 0), Drawing(MockSurface()))
    ).draw_on_screens
    assert StaticScene(
        (DrawOnScreen(Coordinate(0, 0), Drawing(MockSurface())),)
    ).draw_on_screens
