from test.util import MockEventfulScene, MockScene, MockSurface
from unittest.mock import PropertyMock

from pytest import raises
from pytest_mock import MockerFixture

from nextrpg import (
    Coordinate,
    Drawing,
    SayEventConfig,
    SayEventScene,
    Size,
    Text,
)


def test_say_event_scene(mocker: MockerFixture) -> None:
    mocker.patch("nextrpg.scene.say_event_scene.FadeInAddOn")
    mocker.patch.object(
        Text, "size", new_callable=PropertyMock, return_value=Size(1, 1)
    )
    assert SayEventScene(
        scene=MockEventfulScene(),
        generator=lambda *_: None,
        character_or_scene=MockScene(),
        message="abc",
        arg=SayEventConfig(),
    ).draw_on_screens
    assert SayEventScene(
        scene=MockEventfulScene(),
        generator=lambda *_: None,
        character_or_scene=MockScene(),
        message="abc",
        arg=None,
    ).draw_on_screens
    assert SayEventScene(
        scene=MockEventfulScene(),
        generator=lambda *_: None,
        character_or_scene=MockScene(),
        message="abc",
        arg=Coordinate(0, 0),
    ).draw_on_screens
    assert SayEventScene(
        scene=MockEventfulScene(),
        generator=lambda *_: None,
        character_or_scene=MockScene(),
        message="abc",
        arg=Drawing(MockSurface()),
    ).draw_on_screens

    with raises(ValueError):
        SayEventScene(
            scene=MockEventfulScene(),
            generator=lambda *_: None,
            character_or_scene=MockScene(),
            message="abc",
            arg="",
        )
