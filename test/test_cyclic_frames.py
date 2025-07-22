from test.util import MockSurface

from nextrpg import CyclicFrames, Drawing


def test_cyclic_frames() -> None:
    frames = CyclicFrames(
        frames=tuple(Drawing(MockSurface(x)) for x in ("a", "b", "c")),
        duration_per_frame=5,
    )
    assert frames.drawing._surface.data == "a"
    assert frames.tick(1).tick(4).drawing._surface.data == "b"
    assert frames.tick(6).reset.drawing._surface.data == "a"
    assert frames.drawings
