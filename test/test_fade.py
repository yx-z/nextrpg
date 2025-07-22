from nextrpg import Coordinate, DrawOnScreen, Drawing, FadeIn, FadeOut
from test.util import MockSurface, MockAnimatedOnScreen


def test_fade() -> None:
    fade_out = FadeOut(
        resource=DrawOnScreen(Coordinate(0, 0), Drawing(MockSurface()))
    )
    assert fade_out.draw_on_screens
    assert not fade_out.tick(99999).tick(999999).draw_on_screens
    assert not fade_out.tick(9).tick(99).tick(999).draw_on_screens

    fade_in = FadeIn(
        resource=(DrawOnScreen(Coordinate(0, 0), Drawing(MockSurface())),)
    )
    assert not fade_in.draw_on_screens
    assert fade_in.tick(9).draw_on_screens
    assert fade_in.tick(9).tick(999999999).draw_on_screens

    assert FadeIn(resource=(MockAnimatedOnScreen(),)).tick(1).draw_on_screens
    assert FadeOut(resource=MockAnimatedOnScreen()).tick(1).draw_on_screens
    assert not FadeOut(resource=()).tick(1).draw_on_screens
