from test.util import MockSurface

from nextrpg import (
    Coordinate,
    Drawing,
    DrawOnScreen,
    StaticScene,
    TransitioningScene,
    TransitionScene,
)


def test_transition_scene():
    scene1 = TransitioningScene()
    scene2 = StaticScene()
    scene3 = TransitioningScene()
    object.__setattr__(
        scene1,
        "draw_on_screens",
        (DrawOnScreen(Coordinate(0, 0), Drawing(MockSurface())),),
    )
    object.__setattr__(
        scene2,
        "draw_on_screens",
        (DrawOnScreen(Coordinate(0, 0), Drawing(MockSurface())),),
    )
    object.__setattr__(
        scene3,
        "draw_on_screens",
        (DrawOnScreen(Coordinate(0, 0), Drawing(MockSurface())),),
    )
    transition = TransitionScene(
        from_scene=scene1,
        intermediary=scene2,
        to_scene=scene3,
        duration=10,
    )
    assert transition.draw_on_screens
    assert transition.tick(1).tick(2).tick(3).draw_on_screens
    assert transition.tick(1).tick(2).tick(3).tick(4).tick(5).tick(60000)
