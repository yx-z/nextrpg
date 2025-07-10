from nextrpg.character.npcs import NpcOnScreen, NpcSpec
from test.util import MockCharacterDrawing
from nextrpg.coordinate import Coordinate
from pytest import raises


def test_character_on_screen() -> None:
    npc = NpcOnScreen(
        spec=NpcSpec(
            name="", character=MockCharacterDrawing(), event=lambda *_: None
        ),
        coordinate=Coordinate(0, 0),
    )
    assert npc.say
    assert npc.coordinate
    assert getattr(npc, "_nextrpg_instance_init")
    with raises(AttributeError):
        npc.dummy_attr
