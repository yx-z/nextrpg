from nextrpg import Typewriter
from test.util import MockTextOnScreen


def test_typewriter() -> None:
    typewriter = Typewriter(text_on_screen=MockTextOnScreen(), delay=10)
    assert typewriter.tick(10).tick(20).draw_on_screens

    typewriter = Typewriter(
        text_on_screen=MockTextOnScreen(
            message="123\n4 5                  6\n"
        ),
        delay=1,
    )
    assert typewriter.tick(5).tick(2).tick(2).draw_on_screens

    typewriter = Typewriter(
        text_on_screen=MockTextOnScreen(message="\n\n\n"), delay=1
    )
    assert typewriter.tick(5).tick(2).tick(2).draw_on_screens
