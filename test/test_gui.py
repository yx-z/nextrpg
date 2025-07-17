from pytest import raises
from pygame import Event, KEYDOWN, K_F1, K_LEFT, VIDEORESIZE
from pytest_mock import MockerFixture

from nextrpg import (
    Config,
    DebugConfig,
    GuiConfig,
    GuiMode,
    ResizeMode,
    Size,
    DrawOnScreen,
    Drawing,
    Coordinate,
    GuiResize,
    KeyPressDown,
    KeyPressUp,
    Window,
    config,
    gui_size,
    Logger,
)
from test.util import MockSurface, override_config


@override_config(Config(GuiConfig(size=Size(10, 10))))
def test_gui(mocker: MockerFixture) -> None:
    mocker.patch("nextrpg.gui.window.init")
    mocker.patch("nextrpg.gui.window.set_caption")
    mocker.patch("nextrpg.gui.window.set_mode")
    mocker.patch("nextrpg.gui.window.Surface", MockSurface)
    mocker.patch("nextrpg.gui.window.flip")
    mocker.patch("nextrpg.gui.window.smoothscale", lambda surf, _: surf)
    window = Window(
        current_config=GuiConfig(Size(10, 20)),
        last_config=GuiConfig(Size(10, 10)),
    )
    drawing = window._scale(
        (DrawOnScreen(Coordinate(0, 0), Drawing(MockSurface())),)
    )
    assert drawing.top_left == Coordinate(280, 0)

    window = window.event(GuiResize(Event(VIDEORESIZE, w=200, h=300)))
    assert window.current_config.size == Size(200, 300)

    draw_debug = window._draw_log
    object.__setattr__(window, "_draw_log", lambda _: None)
    window.draw((), 0)
    window._screen.blits.assert_not_called()
    object.__setattr__(window, "_draw_log", draw_debug)

    window2 = Window(
        current_config=GuiConfig(resize_mode=ResizeMode.KEEP_NATIVE_SIZE)
    )
    window2.draw((), 0)
    window2._screen.blit.assert_called()

    assert Window(
        current_config=GuiConfig(allow_window_resize=False)
    )._current_gui_flag

    Window(current_config=GuiConfig(resize_mode="Invalid resize mode")).draw(
        (), 0
    )
    Window(
        current_config=window.current_config,
        last_config=window.current_config,
        initial_config=window.current_config,
        _title="screen",
        _screen=MockSurface(),
    )

    assert window.event(KeyPressUp(Event(KEYDOWN, key=K_LEFT))) is window
    assert window.event(KeyPressDown(Event(KEYDOWN, key=K_LEFT))) is window
    assert window.current_config.gui_mode is GuiMode.WINDOWED
    assert (
        window.event(
            KeyPressDown(Event(KEYDOWN, key=K_F1))
        ).current_config.gui_mode
        is GuiMode.FULL_SCREEN
    )

    assert window._resize(window.current_config.size) is window

    with override_config(Config(debug=DebugConfig())):
        Logger("TestGuiLogger").debug("test")
        window._draw_log(0)

    assert window.update
    with override_config(Config(gui=GuiConfig(allow_window_resize=True))):
        assert Window(
            current_config=GuiConfig(allow_window_resize=False)
        ).update
        assert Window(current_config=config().gui).update


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
