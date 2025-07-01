from pygame import Event, KEYDOWN, K_F1, K_LEFT, VIDEORESIZE
from pytest_mock import MockerFixture

from nextrpg.config import Config, DebugConfig, GuiConfig, GuiMode
from nextrpg.core import Size
from nextrpg.draw_on_screen import Coordinate, DrawOnScreen, Drawing
from nextrpg.event.pygame_event import GuiResize, KeyPressDown, KeyPressUp
from nextrpg.gui import Gui, _resize
from nextrpg.logger import clear_debug_logs, debug_log
from test.util import MockSurface, override_config


@override_config(Config(GuiConfig(size=Size(10, 10))))
def test_gui(mocker: MockerFixture) -> None:
    mocker.patch("nextrpg.gui.init")
    mocker.patch("nextrpg.gui.set_caption")
    mocker.patch("nextrpg.gui.set_mode")
    mocker.patch("nextrpg.gui.Surface", MockSurface)
    mocker.patch("nextrpg.gui.flip")
    mocker.patch("nextrpg.gui.scale", lambda surf, _: surf)
    gui = Gui(
        current_config=GuiConfig(Size(10, 20)),
        last_config=GuiConfig(Size(10, 10)),
    )
    drawing = gui._scale(
        [DrawOnScreen(Coordinate(0, 0), Drawing(MockSurface()))]
    )
    assert drawing.top_left == Coordinate(280, 0)

    gui = gui.event(GuiResize(Event(VIDEORESIZE, w=200, h=300)))
    assert gui.current_config.size == Size(200, 300)

    draw_debug = gui._draw_debug_log
    with override_config(Config(GuiConfig(resize_mode="INVALID"))):
        gui._draw_debug_log = lambda: None
        gui.draw([])
        gui._screen.blits.assert_not_called()
    gui._draw_debug_log = draw_debug

    assert gui.event(KeyPressUp(Event(KEYDOWN, key=K_LEFT))) is gui
    assert gui.event(KeyPressDown(Event(KEYDOWN, key=K_LEFT))) is gui
    assert gui.current_config.gui_mode is GuiMode.WINDOWED
    assert (
        gui.event(
            KeyPressDown(Event(KEYDOWN, key=K_F1))
        ).current_config.gui_mode
        is GuiMode.FULL_SCREEN
    )

    debug_log("a")
    with override_config(Config(debug=DebugConfig())):
        gui._draw_debug_log()
        gui._screen.blits.assert_called()
    clear_debug_logs()

    width, height = gui.current_config.size
    assert _resize(gui, GuiResize(Event(w=width, h=height))) is gui
