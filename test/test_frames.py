from dataclasses import dataclass

from nextrpg.draw_on_screen import Drawing
from nextrpg.frames import CyclicFrames


@dataclass(frozen=True)
class MockDrawing(Drawing):
    data: str


def test_cyclic_frames() -> None:
    frames = CyclicFrames(
        [MockDrawing(x) for x in ["a", "b", "c"]], frame_duration=5
    )
    assert frames.current_frame == MockDrawing("a")
    assert frames.peek(1) == MockDrawing("a")
    assert frames.peek(5) == MockDrawing("b")
    assert frames.peek(10) == MockDrawing("c")
    assert frames.peek(20) == MockDrawing("b")
    assert frames.step(1).step(4).current_frame == MockDrawing("b")
    assert frames.step(6).reset().current_frame == MockDrawing("a")
