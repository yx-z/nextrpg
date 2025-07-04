from nextrpg.event.move import Move
from nextrpg.scene.scene import Scene
from test.util import MockCharacterDrawing


def test_move() -> None:
    scene = Scene()
    move = Move("", "", lambda _, __: scene)
    assert move.to_scene(MockCharacterDrawing()) is scene
