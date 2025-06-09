from dataclasses import dataclass

from pytest_mock import MockerFixture

from nextrpg.draw_on_screen import Drawing
from nextrpg.frames import FrameExhaustedOption, Frames


def test_frame_exhausted_option() -> None:
    assert len(FrameExhaustedOption) == 3


@dataclass(frozen=True)
class MockDrawing(Drawing):
    data: str


def test_keep_last_frame(mocker: MockerFixture) -> None:
    mocker.patch("nextrpg.frames.Drawing", MockDrawing)
    frames = Frames(
        [MockDrawing("a"), MockDrawing("b")],
        FrameExhaustedOption.KEEP_LAST_FRAME,
    )
    assert frames.current_frame() == MockDrawing("a")
    assert frames.next_frame() == MockDrawing("b")
    assert frames.next_frame() == MockDrawing("b")
    assert frames.current_frame() == MockDrawing("b")

    frames.reset()
    assert frames.current_frame() == MockDrawing("a")
    assert frames.next_frame() == MockDrawing("b")
    assert frames.next_frame() == MockDrawing("b")
    assert frames.current_frame() == MockDrawing("b")


def test_cycle(mocker: MockerFixture) -> None:
    mocker.patch("nextrpg.frames.Drawing", MockDrawing)
    frames = Frames(
        [MockDrawing("a"), MockDrawing("b"), MockDrawing("c")],
        FrameExhaustedOption.CYCLE,
    )
    assert frames.current_frame() == MockDrawing("a")
    assert frames.next_frame() == MockDrawing("b")
    assert frames.current_frame() == MockDrawing("b")
    assert frames.next_frame() == MockDrawing("c")
    assert frames.next_frame() == MockDrawing("a")
    assert frames.next_frame() == MockDrawing("b")
    assert frames.current_frame() == MockDrawing("b")

    frames.reset()
    assert frames.current_frame() == MockDrawing("a")
    assert frames.next_frame() == MockDrawing("b")
    assert frames.next_frame() == MockDrawing("c")


def test_disappear(mocker: MockerFixture) -> None:
    mocker.patch("nextrpg.frames.Drawing", MockDrawing)
    frames = Frames(
        [MockDrawing("a"), MockDrawing("b")], FrameExhaustedOption.DISAPPEAR
    )
    assert frames.current_frame() == MockDrawing("a")
    assert frames.next_frame() == MockDrawing("b")
    assert not frames.next_frame()
    assert not frames.next_frame()
    assert not frames.current_frame()

    frames.reset()
    assert frames.current_frame() == MockDrawing("a")
    assert frames.next_frame() == MockDrawing("b")
    assert not frames.next_frame()
