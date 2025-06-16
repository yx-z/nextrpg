from dataclasses import dataclass

from pygame import Surface

from nextrpg.draw_on_screen import Drawing
from nextrpg.frames import CyclicFrames


@dataclass(frozen=True)
class MockSurface(Surface):
    data: str


def test_cyclic_frames() -> None:
    frames = CyclicFrames(
        [Drawing(MockSurface(x)) for x in ["a", "b", "c"]], duration_per_frame=5
    )
    assert frames.current_frame == Drawing(MockSurface("a"))
    assert frames.step(1).step(4).current_frame == Drawing(MockSurface("b"))
    assert frames.step(6).reset().current_frame == Drawing(MockSurface("a"))
