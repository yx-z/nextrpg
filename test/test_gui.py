from _pytest.raises import raises
from pygame import Event, KEYDOWN, K_F1, K_LEFT, VIDEORESIZE
from pytest_mock import MockerFixture

from nextrpg.config import Config, DebugConfig, GuiConfig, GuiMode, ResizeMode
from nextrpg.core import Size
from nextrpg.draw_on_screen import DrawOnScreen
from nextrpg.drawing import Drawing
from nextrpg.coordinate import Coordinate
from nextrpg.event.pygame_event import GuiResize, KeyPressDown, KeyPressUp
from nextrpg.gui import Gui, _resize, gui_size
from nextrpg.logger import Logger
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

    draw_debug = gui._draw_log
    object.__setattr__(gui, "_draw_log", lambda _: None)
    gui.draw([], 0)
    gui._screen.blits.assert_not_called()
    object.__setattr__(gui, "_draw_log", draw_debug)

    gui2 = Gui(GuiConfig(resize_mode=ResizeMode.KEEP_NATIVE_SIZE))
    gui2.draw([], 0)
    gui2._screen.blit.assert_called()

    Gui(GuiConfig(resize_mode="Invalid resize mode")).draw([], 0)
    Gui(gui.current_config, gui.current_config, gui.current_config, "screen")

    assert gui.event(KeyPressUp(Event(KEYDOWN, key=K_LEFT))) is gui
    assert gui.event(KeyPressDown(Event(KEYDOWN, key=K_LEFT))) is gui
    assert gui.current_config.gui_mode is GuiMode.WINDOWED
    assert (
        gui.event(
            KeyPressDown(Event(KEYDOWN, key=K_F1))
        ).current_config.gui_mode
        is GuiMode.FULL_SCREEN
    )

    width, height = gui.current_config.size
    assert _resize(gui, GuiResize(Event(VIDEORESIZE, w=width, h=height))) is gui

    with override_config(Config(debug=DebugConfig())):
        Logger("TestGuiLogget").debug("test")
        gui._draw_log(0)


def test_gui_size() -> None:
    with override_config(Config(GuiConfig(resize_mode=ResizeMode.SCALE))):
        assert gui_size() == Size(1280, 720)

    with override_config(
        Config(GuiConfig(resize_mode=ResizeMode.KEEP_NATIVE_SIZE))
    ):
        assert gui_size() == Size(1280, 720)

    with raises(ValueError), override_config(
        Config(GuiConfig(resize_mode="INVALID"))
    ):
        gui_size()
