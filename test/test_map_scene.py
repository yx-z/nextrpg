from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator
from unittest.mock import MagicMock, Mock

from pygame import Event, QUIT
from pytest_mock import MockerFixture

from nextrpg.event.pygame_event import Quit
from nextrpg.scene.map_scene import MapScene
from test.util import MockCharacterDrawing, MockSurface


@dataclass(frozen=True)
class MockTmx:
    name: str
    tilewidth: int = 10
    tileheight: int = 11
    x: int = 1
    y: int = 2
    layers: list["MockTmx"] = field(default_factory=list)
    properties: dict = field(default_factory=dict)
    tile_properties: dict = field(default_factory=dict)
    data: MagicMock = MagicMock()

    def __iter__(self) -> Iterator["MockTmx"]:
        return iter(self.layers)

    def tiles(self) -> list[tuple[int, int, MockSurface]]:
        return [(100, 200, MockSurface("a"))]


def test_map_scene(mocker: MockerFixture) -> None:
    mocker.patch(
        "nextrpg.scene.map_scene.load_pygame",
        lambda name: MockTmx(
            name,
            layers=[
                MockTmx("foreground"),
                MockTmx("object", layers=[MockTmx("player")]),
            ],
        ),
    )
    map = MapScene.load(Path("test"), MockCharacterDrawing())
    assert map.event(Quit(Event(QUIT)))
    assert map.step(1).draw_on_screen
