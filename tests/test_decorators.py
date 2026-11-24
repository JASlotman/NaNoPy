from __future__ import annotations

import importlib
import os
import sys
import types
import unittest
from typing import TYPE_CHECKING, Any, ClassVar
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from NaNoPy.classes.frame import Frame
from NaNoPy.constants import DEFAULT_PNG_LEVEL, PNG_LEVEL_MIN, PNG_LEVEL_SMALL

decorators = importlib.import_module("NaNoPy.decorators")

if TYPE_CHECKING:
    from collections.abc import Callable


class FakeMovieWriter:
    def __init__(self) -> None:
        self.is_recording = True
        self.count = 0

    def add_frame(self, frame: Frame) -> None:
        self.count += 1

    def frame_count(self) -> int:
        return self.count

    def clear(self) -> None:
        self.is_recording = False


class FakeMainloop:
    def __init__(self) -> None:
        self.stopped = False

    def stop(self) -> None:
        self.stopped = True


class FakeCanvas:
    latest: ClassVar[FakeCanvas | None] = None

    def __init__(self, *args: object, **kwargs: object) -> None:
        FakeCanvas.latest = self
        self.movie = FakeMovieWriter()
        self.NNP = FakeMainloop()
        self.present_count = 0
        self.capture_count = 0
        self.png_levels: list[int | None] = []

    def start_recording(self, output_path: str, fps: int, codec: str) -> FakeMovieWriter:
        return self.movie

    def stop_recording(self) -> FakeMovieWriter:
        self.movie.is_recording = False
        return self.movie

    def save_recording(self) -> str:
        return "animation.mp4"

    def clear(self) -> None:
        pass

    def update(self) -> None:
        self.present_count += 1

    def update_embedded(self, png_level: int | None = None) -> Frame:
        self.capture_count += 1
        self.png_levels.append(png_level)
        frame = Frame.black(1, 1, png_level=png_level)
        if self.movie.is_recording:
            self.movie.add_frame(frame)
        return frame


class DecoratorRecordingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.displayed: list[Frame] = []

    def run_loop(self, callback: Callable[..., object], *, embedded: bool, **loop_options: Any) -> FakeCanvas:
        # loop() imports display/clear_output from IPython.display when it is called, so the
        # stand-in has to live in sys.modules. That keeps these tests independent of IPython
        # (an optional extra) and lets them see exactly which frames were displayed.
        ipython_display = types.SimpleNamespace(display=self.displayed.append, clear_output=lambda *args, **kwargs: None)
        with (
            patch.dict(sys.modules, {"ipykernel": object(), "IPython.display": ipython_display}),
            patch.object(decorators, "Canvas", FakeCanvas),
            patch.object(decorators, "Writer", lambda canvas: object()),
            patch("builtins.print"),
        ):
            decorate = decorators.loop(
                frame_count=1,
                embedded=embedded,
                record_mp4="animation.mp4",
                **loop_options,
            )
            decorate(callback)
            assert FakeCanvas.latest is not None
            return FakeCanvas.latest

    def test_non_embedded_loop_captures_when_callback_does_not(self) -> None:
        canvas = self.run_loop(lambda screen, pen, index: None, embedded=False)
        self.assertEqual(canvas.present_count, 1)
        self.assertEqual(canvas.capture_count, 1)
        self.assertEqual(canvas.movie.frame_count(), 1)

    def test_non_embedded_loop_does_not_duplicate_callback_capture(self) -> None:
        def callback(screen: Any, pen: Any, index: int) -> Frame:
            return screen.update_embedded()

        canvas = self.run_loop(callback, embedded=False)
        self.assertEqual(canvas.present_count, 1)
        self.assertEqual(canvas.capture_count, 1)
        self.assertEqual(canvas.movie.frame_count(), 1)

    def test_embedded_loop_does_not_duplicate_returned_capture(self) -> None:
        def callback(screen: Any, pen: Any, index: int) -> Frame:
            return screen.update_embedded()

        canvas = self.run_loop(callback, embedded=True)
        self.assertEqual(canvas.capture_count, 1)
        self.assertEqual(canvas.movie.frame_count(), 1)

    def test_embedded_loop_forwards_png_level_to_the_captured_frame(self) -> None:
        canvas = self.run_loop(lambda screen, pen, index: None, embedded=True, png_level=PNG_LEVEL_SMALL)

        self.assertEqual(canvas.png_levels, [PNG_LEVEL_SMALL])
        self.assertEqual([frame.png_level for frame in self.displayed], [PNG_LEVEL_SMALL])

    def test_embedded_loop_without_png_level_displays_at_the_default(self) -> None:
        canvas = self.run_loop(lambda screen, pen, index: None, embedded=True)

        self.assertEqual(canvas.png_levels, [None])
        self.assertEqual([frame.png_level for frame in self.displayed], [DEFAULT_PNG_LEVEL])

    def test_png_level_is_applied_to_a_frame_returned_by_the_callback(self) -> None:
        returned = Frame.black(1, 1, png_level=DEFAULT_PNG_LEVEL)

        self.run_loop(lambda screen, pen, index: returned, embedded=True, png_level=PNG_LEVEL_MIN)

        self.assertEqual(len(self.displayed), 1)
        self.assertIs(self.displayed[0], returned)
        self.assertEqual(returned.png_level, PNG_LEVEL_MIN)

    def test_loop_without_png_level_leaves_a_returned_frames_own_level_alone(self) -> None:
        returned = Frame.black(1, 1, png_level=PNG_LEVEL_SMALL)

        self.run_loop(lambda screen, pen, index: returned, embedded=True)

        self.assertEqual(returned.png_level, PNG_LEVEL_SMALL)

    def test_invalid_png_level_is_rejected_before_a_canvas_is_created(self) -> None:
        FakeCanvas.latest = None

        with self.assertRaises(ValueError):
            self.run_loop(lambda screen, pen, index: None, embedded=True, png_level=99)

        self.assertIsNone(FakeCanvas.latest, "a rejected level must not leave a window open")


if __name__ == "__main__":
    unittest.main()
