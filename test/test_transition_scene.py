from test.util import MockScene, MockSurface

from nextrpg import Coordinate, Draw, DrawOnScreen, TransitionScene


def test_transition_scene():
    scene1 = MockScene()
    scene3 = MockScene()
    object.__setattr__(
        scene1,
        "draw_on_screens",
        (DrawOnScreen(Coordinate(0, 0), Draw(MockSurface())),),
    )
    object.__setattr__(
        scene3,
        "draw_on_screens",
        (DrawOnScreen(Coordinate(0, 0), Draw(MockSurface())),),
    )
    transition = TransitionScene(
        from_scene=scene1,
        to_scene=scene3,
        duration=10,
    )
    assert transition.draw_on_screens
    assert transition.tick(1).tick(2).tick(3).draw_on_screens
    assert transition.tick(1).tick(2).tick(3).tick(4).tick(5).tick(60000)

    transition2 = TransitionScene(
        from_scene=scene1,
        to_scene=scene3,
        duration=10,
        intermediary=DrawOnScreen(Coordinate(0, 0), Draw(MockSurface())),
    )
    assert transition2.tick(1).draw_on_screens
