from pytest_mock import MockerFixture

from nextrpg.config import Config, GuiConfig
from nextrpg.core import Coordinate, Size
from nextrpg.draw_on_screen import DrawOnScreen, Drawing
from nextrpg.gui import Gui
from test.util import MockSurface, override_config


@override_config(Config(GuiConfig(size=Size(10, 10))))
def test_gui(mocker: MockerFixture) -> None:
    mocker.patch("nextrpg.gui.Surface")
    mocker.patch("nextrpg.gui.smoothscale")
    gui = Gui(Size(10, 20))
    _, center = gui.scale(
        [DrawOnScreen(Coordinate(0, 0), Drawing(MockSurface()))]
    )
    assert center == (0.0, 5.0)
