from pygame import Event, VIDEORESIZE
from pytest_mock import MockerFixture

from nextrpg.config import Config, GuiConfig, GuiMode, ResizeMode
from nextrpg.core import Coordinate, Size
from nextrpg.draw_on_screen import DrawOnScreen, Drawing
from nextrpg.event.pygame_event import GuiResize
from nextrpg.gui import Gui, _gui_flag
from test.util import MockSurface, override_config


@override_config(Config(GuiConfig(size=Size(10, 10))))
def test_gui(mocker: MockerFixture) -> None:
    mocker.patch("nextrpg.gui.init")
    mocker.patch("nextrpg.gui.set_caption")
    mocker.patch("nextrpg.gui.set_mode")
    mocker.patch("nextrpg.gui.Surface")
    mocker.patch("nextrpg.gui.smoothscale")
    mocker.patch("nextrpg.gui.flip")
    mocker.patch("nextrpg.gui.get_window_size", return_value=(20, 30))
    gui = Gui(Size(10, 20))
    drawing = gui._scale(
        [DrawOnScreen(Coordinate(0, 0), Drawing(MockSurface()))]
    )
    assert drawing.top_left == Coordinate(0.0, 5.0)
    assert Gui.current_size() == Size(20, 30)

    gui = gui.resize(GuiResize(Event(VIDEORESIZE, w=200, h=300)))
    assert gui.window == Size(200, 300)

    gui.draw([])
    gui._screen.blit.assert_called()

    with override_config(Config(GuiConfig(resize_mode=ResizeMode.KEEP_NATIVE))):
        gui.draw([])
        gui._screen.blits.assert_called()


@override_config(
    Config(GuiConfig(allow_window_resize=False, gui_mode=GuiMode.FULL_SCREEN))
)
def test_gui_flag() -> None:
    assert _gui_flag() == -2147483648
