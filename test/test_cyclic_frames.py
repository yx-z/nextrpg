from test.util import MockSurface

from nextrpg import CyclicFrames, Draw


def test_cyclic_frames() -> None:
    frames = CyclicFrames(
        frames=tuple(Draw(MockSurface(x)) for x in ("a", "b", "c")),
        duration_per_frame=5,
    )
    assert frames.draw._surface.data == "a"
    assert frames.tick(1).tick(4).draw._surface.data == "b"
    assert frames.tick(6).reset.draw._surface.data == "a"
    assert frames.draw
