import ctypes
import importlib
import os
import threading
import unittest
from typing import Any
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from NaNoPy.classes.frame import Frame
from NaNoPy.constants import DEFAULT_PNG_LEVEL, PNG_LEVEL_MIN, PNG_LEVEL_SMALL

mainloop_module = importlib.import_module("NaNoPy.classes.mainloop")
Mainloop = mainloop_module.Mainloop


class FakeCanvas:
    window = object()
    renderer = object()
    _reload_fonts = False

    @staticmethod
    def get_window_size() -> tuple[int, int]:
        return (2, 1)


class CollectingWriter:
    is_recording = True

    def __init__(self, error: BaseException | None = None) -> None:
        self.frames: list[Frame] = []
        self.error = error

    def add_frame(self, image: Frame) -> None:
        if self.error is not None:
            raise self.error
        self.frames.append(image)


class EmbeddedCaptureTests(unittest.TestCase):
    def make_loop(self, writer: CollectingWriter) -> Mainloop:
        loop = Mainloop.__new__(Mainloop)
        loop.running = True
        loop._sdl_initialized = True
        loop._runtime_thread_id = threading.get_ident()
        loop.multiple_windows = False
        loop._movie_writer = writer
        loop._handle_events = lambda: True
        return loop

    @staticmethod
    def render_two_pixels(renderer: Any, rect: Any, pixel_format: Any, pixels: Any, pitch: Any) -> int:
        values = bytes((255, 0, 0, 255, 0, 255, 0, 128))
        ctypes.memmove(pixels, values, len(values))
        return 0

    def test_raw_rgba_capture_reaches_frame_and_writer_once(self) -> None:
        writer = CollectingWriter()
        loop = self.make_loop(writer)

        with patch.object(mainloop_module, "SDL_RenderReadPixels", side_effect=self.render_two_pixels):
            image = loop.update_embedded(FakeCanvas())

        self.assertIsInstance(image, Frame)
        self.assertEqual(image.size, (2, 1))
        self.assertEqual(image.mode, "RGBA")
        self.assertEqual(image.getpixel((0, 0)), (255, 0, 0, 255))
        self.assertEqual(image.getpixel((1, 0)), (0, 255, 0, 128))
        self.assertEqual(image.tobytes(), bytes((255, 0, 0, 255, 0, 255, 0, 128)))
        self.assertEqual(len(writer.frames), 1)
        self.assertIs(writer.frames[0], image)

    def test_png_level_defaults_and_can_be_chosen_per_capture(self) -> None:
        loop = self.make_loop(CollectingWriter())

        with patch.object(mainloop_module, "SDL_RenderReadPixels", side_effect=self.render_two_pixels):
            default = loop.update_embedded(FakeCanvas())
            small = loop.update_embedded(FakeCanvas(), png_level=PNG_LEVEL_SMALL)
            fast = loop.update_embedded(FakeCanvas(), PNG_LEVEL_MIN)

        self.assertEqual(default.png_level, DEFAULT_PNG_LEVEL)
        self.assertEqual(small.png_level, PNG_LEVEL_SMALL)
        self.assertEqual(fast.png_level, PNG_LEVEL_MIN)

    def test_invalid_png_level_is_rejected_instead_of_becoming_a_black_frame(self) -> None:
        loop = self.make_loop(CollectingWriter())
        canvas = FakeCanvas()

        with patch.object(mainloop_module, "SDL_RenderReadPixels", side_effect=self.render_two_pixels) as read_pixels:
            with self.assertRaises(ValueError):
                loop.update_embedded(canvas, png_level=10)
            with self.assertRaises(TypeError):
                loop.update_embedded(canvas, png_level="fast")  # type: ignore[arg-type]

        read_pixels.assert_not_called()

    def test_failed_capture_warns_and_returns_a_black_frame_that_is_not_recorded(self) -> None:
        writer = CollectingWriter()
        loop = self.make_loop(writer)

        with (
            patch.object(mainloop_module, "SDL_RenderReadPixels", return_value=1),
            patch.object(mainloop_module, "SDL_GetError", return_value=b"read failed"),
            self.assertWarnsRegex(RuntimeWarning, "read failed"),
        ):
            frame = loop.update_embedded(FakeCanvas(), png_level=PNG_LEVEL_MIN)

        self.assertEqual(frame.size, (2, 1))
        self.assertEqual(frame.getpixel((0, 0)), (0, 0, 0, 255))
        self.assertEqual(frame.png_level, PNG_LEVEL_MIN)
        self.assertEqual(writer.frames, [])

    def test_encoder_error_is_not_swallowed_by_render_fallback(self) -> None:
        writer = CollectingWriter(RuntimeError("broken ffmpeg pipe"))
        loop = self.make_loop(writer)
        canvas = FakeCanvas()

        with patch.object(mainloop_module, "SDL_RenderReadPixels", side_effect=self.render_two_pixels):
            expected_message = "broken ffmpeg pipe"
            with self.assertRaisesRegex(RuntimeError, expected_message):
                loop.update_embedded(canvas)


if __name__ == "__main__":
    unittest.main()
