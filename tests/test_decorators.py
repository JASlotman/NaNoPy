from __future__ import annotations

import importlib
import os
import sys
import unittest
from typing import TYPE_CHECKING, Any, ClassVar
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from PIL import Image

decorators = importlib.import_module("NaNoPy.decorators")

if TYPE_CHECKING:
    from collections.abc import Callable


class FakeMovieWriter:
    def __init__(self) -> None:
        self.is_recording = True
        self.count = 0

    def add_frame(self, frame: Image.Image) -> None:
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

    def update_embedded(self) -> Image.Image:
        self.capture_count += 1
        image = Image.new("RGBA", (1, 1))
        if self.movie.is_recording:
            self.movie.add_frame(image)
        return image


class DecoratorRecordingTests(unittest.TestCase):
    def run_loop(self, callback: Callable[..., object], *, embedded: bool) -> FakeCanvas:
        with (
            patch.dict(sys.modules, {"ipykernel": object()}),
            patch.object(decorators, "Canvas", FakeCanvas),
            patch.object(decorators, "Writer", lambda canvas: object()),
            patch.object(decorators, "clear_output", create=True),
            patch.object(decorators, "display", create=True),
            patch.object(decorators, "Image", Image, create=True),
            patch("builtins.print"),
        ):
            decorate = decorators.loop(
                frame_count=1,
                embedded=embedded,
                record_mp4="animation.mp4",
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
        def callback(screen: Any, pen: Any, index: int) -> Image.Image:
            return screen.update_embedded()

        canvas = self.run_loop(callback, embedded=False)
        self.assertEqual(canvas.present_count, 1)
        self.assertEqual(canvas.capture_count, 1)
        self.assertEqual(canvas.movie.frame_count(), 1)

    def test_embedded_loop_does_not_duplicate_returned_capture(self) -> None:
        def callback(screen: Any, pen: Any, index: int) -> Image.Image:
            return screen.update_embedded()

        canvas = self.run_loop(callback, embedded=True)
        self.assertEqual(canvas.capture_count, 1)
        self.assertEqual(canvas.movie.frame_count(), 1)


if __name__ == "__main__":
    unittest.main()
