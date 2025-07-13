from dataclasses import dataclass
from enum import Enum, auto

from nextrpg.core import BLACK, Rgba, Size


class ResizeMode(Enum):
    """
    Resize mode enum.

    Attributes:
        `SCALE`: Scale the images to fit the GUI size.

        `KEEP_NATIVE_SIZE`: Keep the native image size.
    """

    SCALE = auto()
    KEEP_NATIVE_SIZE = auto()


class GuiMode(Enum):
    """
    Gui mode enum.

    Attributes:
        `WINDOWED`: Windowed GUI.

        `FULL_SCREEN`: Full screen GUI.
    """

    WINDOWED = auto()
    FULL_SCREEN = auto()

    @property
    def opposite(self) -> GuiMode:
        """
        Get the opposite gui mode.

        Returns:
            `GuiMode`: The opposite gui mode.
        """
        return _OPPOSITE_GUI_MODE[self]


@dataclass(frozen=True)
class GuiConfig:
    """
    Configuration class for Graphical User Interface (GUI).

    This is used by `nextrpg.gui.Gui` to initialize
    the pygame window and by the rendering system to control display properties.

    Attributes:
        `title`: The title of the GUI window.

        `size`: The resolution or dimensions of the GUI window defined
            by width and height. This also defines the aspect ratio of the game.

        `frames_per_second`: FPS. The target frame rate for the application's
            rendering performance.

        `background_color`: The background color of the GUI window.

        `gui_mode`: Whether to start the game in windowed or full screen mode.

        `resize_mode`: Whether to scale the images to fit the GUI size,
            or keep the native image size.

        `allow_window_resize`: Whether to allow the user to resize the window
            in windowed mode.
    """

    title: str = "nextrpg"
    size: Size = Size(1280, 720)
    frames_per_second: int = 60
    background_color: Rgba = BLACK
    gui_mode: GuiMode = GuiMode.WINDOWED
    resize_mode: ResizeMode = ResizeMode.SCALE
    allow_window_resize: bool = True


_OPPOSITE_GUI_MODE = {
    GuiMode.WINDOWED: GuiMode.FULL_SCREEN,
    GuiMode.FULL_SCREEN: GuiMode.WINDOWED,
}
