from pygame import Event
from pygame.locals import KEYDOWN, K_RETURN, QUIT
from nextrpg import (
    Coordinate,
    DrawOnScreen,
    Drawing,
    FadeInAddOn,
    KeyPressDown,
    Quit,
    SayEventConfig,
)
from test.util import MockTextOnScreen
from test.util import MockEventfulScene, MockSurface


def test_say_event_add_on() -> None:
    fade_in = FadeInAddOn(
        background=(DrawOnScreen(Coordinate(0, 0), Drawing(MockSurface())),),
        text=MockTextOnScreen(),
        config=SayEventConfig(),
        scene=MockEventfulScene(),
        npc_object_name="test",
        initial_coord=Coordinate(0, 0),
        generator=lambda *_: None,
    )
    assert fade_in.tick(1).draw_on_screens

    assert (
        FadeInAddOn(
            background=(
                DrawOnScreen(Coordinate(0, 0), Drawing(MockSurface())),
            ),
            text=MockTextOnScreen(),
            config=SayEventConfig(),
            scene=MockEventfulScene(),
            npc_object_name=None,
            initial_coord=Coordinate(0, 0),
            generator=lambda *_: None,
        )
        .tick(1)
        .draw_on_screens
    )

    assert fade_in.tick(10000).tick(10).draw_on_screens
    assert fade_in.tick(10000).tick(99910).tick(2).draw_on_screens
    enter = KeyPressDown(Event(KEYDOWN, key=K_RETURN))
    assert fade_in.tick(10).tick(10).tick(3099).event(Quit(Event(QUIT)))
    assert (
        fade_in.tick(10).tick(9910).tick(2).event(enter).tick(1).draw_on_screens
    )
    assert fade_in.tick(10).tick(9910).tick(2).event(enter).tick(1).tick(3000)
