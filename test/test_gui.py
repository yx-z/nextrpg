from pygame import Event, KEYDOWN, K_F1, K_LEFT, VIDEORESIZE
from pytest_mock import MockerFixture

from nextrpg.config import Config, GuiConfig, GuiMode, ResizeMode
from nextrpg.core import Size
from nextrpg.draw_on_screen import Coordinate, DrawOnScreen, Drawing
from nextrpg.event.pygame_event import GuiResize, KeyPressDown, KeyPressUp
from nextrpg.gui import Gui, _gui_flag
from test.util import MockSurface, override_config


@override_config(Config(GuiConfig(size=Size(10, 10))))
def test_gui(mocker: MockerFixture) -> None:
    mocker.patch("nextrpg.gui.init")
    mocker.patch("nextrpg.gui.set_caption")
    mocker.patch("nextrpg.gui.set_mode")
    mocker.patch("nextrpg.gui.Surface", MockSurface)
    mocker.patch("nextrpg.gui.flip")
    mocker.patch("nextrpg.gui.scale", lambda surf, _: surf)
    gui = Gui(Size(10, 20))
    drawing = gui._scale(
        [DrawOnScreen(Coordinate(0, 0), Drawing(MockSurface()))]
    )
    assert drawing.top_left == Coordinate(0.0, 5.0)

    gui = gui.event(GuiResize(Event(VIDEORESIZE, w=200, h=300)))
    assert gui.window == Size(200, 300)

    with override_config(Config(GuiConfig(resize_mode="INVALID"))):
        gui.draw([])
        gui._screen.blit.assert_not_called()
        gui._screen.blits.assert_not_called()

    gui.draw([])
    gui._screen.blit.assert_called()

    with override_config(
        Config(GuiConfig(resize_mode=ResizeMode.KEEP_NATIVE_SIZE))
    ):
        gui.draw([])
        gui._screen.blits.assert_called()

    assert gui.event(KeyPressUp(Event(KEYDOWN, key=K_LEFT))) is gui
    assert gui.event(KeyPressDown(Event(KEYDOWN, key=K_LEFT))) is gui
    assert gui._gui_mode is GuiMode.WINDOWED
    assert (
        gui.event(KeyPressDown(Event(KEYDOWN, key=K_F1)))._gui_mode
        is GuiMode.FULL_SCREEN
    )


@override_config(Config(GuiConfig(allow_window_resize=False)))
def test_gui_flag() -> None:
    assert _gui_flag(GuiMode.FULL_SCREEN) == -2147483648
