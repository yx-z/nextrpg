from dataclasses import replace
from functools import cached_property
from test.util import MockCharacterDrawing
from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock

from pygame import K_SPACE, Event
from pygame.locals import K_RETURN, KEYDOWN, QUIT
from pytest_mock import MockerFixture

from nextrpg import (
    CharacterSpec,
    Coordinate,
    Direction,
    EventfulScene,
    KeyPressDown,
    MapScene,
    MovingNpcOnScreen,
    NpcOnScreen,
    NpcSpec,
    PlayerOnScreen,
    Quit,
    Rectangle,
    RpgEventGenerator,
    RpgEventScene,
    Size,
    say,
)


def test_npc_on_screen() -> None:
    npc = NpcOnScreen(
        coordinate=Coordinate(0, 0),
        spec=NpcSpec(
            object_name="name",
            character=MockCharacterDrawing(),
            event=lambda *_: None,
        ),
    ).tick(0)
    assert npc
    assert (
        npc.start_event(
            PlayerOnScreen(
                collisions=(),
                spec=CharacterSpec(
                    object_name="", character=MockCharacterDrawing()
                ),
                coordinate=Coordinate(0, 0),
            )
        ).character.direction
        is Direction.RIGHT
    )


def test_npcs(mocker: MockerFixture) -> None:
    class MockFont:
        @cached_property
        def size(self) -> Size:
            return Size(1, 1)

    assert MockFont().size == Size(1, 1)
    mocker.patch("nextrpg.draw.font.Font.pygame", MockFont)

    def event(p: PlayerOnScreen, *args: Any) -> None:
        res = say(p, "hi")
        assert res
        say(p, "hi")

    map_helper = Mock()
    map_helper.get_object.return_value = SimpleNamespace(
        x=1, y=1, width=1, height=1
    )
    map_helper.foreground = ()
    map_helper.background = ()
    map_helper.above_character = ()
    map_helper.collision_visuals = ()
    map_helper.map_size = Size(100, 100)
    mocker.patch("nextrpg.scene.map_scene.MapHelper", return_value=map_helper)
    mocker.patch(
        "nextrpg.scene.map_scene.MapScene.draw_on_screens_before_shift",
        return_value=(),
    )
    player = PlayerOnScreen(
        spec=CharacterSpec(object_name="", character=MockCharacterDrawing()),
        coordinate=Coordinate(0, 0),
        collisions=(),
    )
    assert not event(player)
    map_scene = MapScene(
        tmx_file="",
        player_spec=CharacterSpec(
            character=MockCharacterDrawing(), object_name=""
        ),
        npcs=(
            NpcOnScreen(
                coordinate=Coordinate(0, 0),
                spec=NpcSpec(
                    object_name="name",
                    character=MockCharacterDrawing(),
                    event=event,
                ),
            ),
            MovingNpcOnScreen(
                coordinate=Coordinate(0, 0),
                spec=NpcSpec(
                    object_name="name",
                    character=MockCharacterDrawing(),
                    event=event,
                ),
                collisions=(),
                path=Rectangle(Coordinate(0, 0), Size(10, 10)),
            ),
        ),
    )
    assert map_scene.npc_dict
    mocker.patch("nextrpg.draw.font.Font.text_size", return_value=Size(1, 1))
    say_event = map_scene.event(KeyPressDown(Event(KEYDOWN, key=K_RETURN)))
    object.__setattr__(say_event.scene, "draw_on_screens", ())
    assert say_event.tick(0)
    assert say_event.event(Quit(Event(QUIT)))
    assert say_event.event(KeyPressDown(Event(KEYDOWN, key=K_SPACE)))
    player = replace(map_scene.player, coordinate=Coordinate(123, 100))
    assert not replace(map_scene, player=player)._collided_npc


def test_eventful_scene() -> None:
    def event() -> RpgEventGenerator:
        yield lambda generator, scene: RpgEventScene(generator, scene)

    gen = event()

    eventful = EventfulScene(
        player=PlayerOnScreen(
            coordinate=Coordinate(0, 0),
            spec=CharacterSpec(
                object_name="", character=MockCharacterDrawing()
            ),
            collisions=(),
        ),
        npcs=(
            NpcOnScreen(
                coordinate=Coordinate(0, 0),
                spec=NpcSpec(
                    object_name="npc",
                    character=MockCharacterDrawing(),
                    event=lambda *_: None,
                ),
            ),
        ),
        _event_generator=gen,
        npc=NpcOnScreen(
            coordinate=Coordinate(0, 0),
            spec=NpcSpec(
                object_name="npc",
                character=MockCharacterDrawing(),
                event=lambda *_: None,
            ),
        ),
    )
    assert eventful.send(gen)
    assert eventful.tick(0)
    assert eventful._next_event

    gen2 = event()
    next(gen2)
    npc = NpcOnScreen(
        spec=NpcSpec(
            object_name="abc",
            event=lambda *_: None,
            character=MockCharacterDrawing(),
        ),
        coordinate=Coordinate(0, 0),
    )
    scene = EventfulScene(
        player=PlayerOnScreen(
            coordinate=Coordinate(0, 0),
            spec=CharacterSpec(
                object_name="", character=MockCharacterDrawing()
            ),
            collisions=(),
        ),
        npc=npc,
        npcs=(npc,),
        _event_generator=gen2,
    )
    assert scene._next_event
