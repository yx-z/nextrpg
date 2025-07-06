from nextrpg.drawing import Drawing
from nextrpg.frames import CyclicFrames
from test.util import MockSurface


def test_cyclic_frames() -> None:
    frames = CyclicFrames(
        frames=[Drawing(MockSurface(x)) for x in ["a", "b", "c"]],
        duration_per_frame=5,
    )
    assert frames.current_frame._surface.data == "a"
    assert frames.tick(1).tick(4).current_frame._surface.data == "b"
    assert frames.tick(6).reset.current_frame._surface.data == "a"
