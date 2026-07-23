import ctypes
import importlib
import os
import threading
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

mainloop_module = importlib.import_module("NaNoPy.classes.mainloop")
Mainloop = mainloop_module.Mainloop


class FakeCanvas:
    window = object()
    renderer = object()
    _reload_fonts = False

    @staticmethod
    def get_window_size():
        return (2, 1)


class CollectingWriter:
    is_recording = True

    def __init__(self, error=None):
        self.frames = []
        self.error = error

    def add_frame(self, image):
        if self.error is not None:
            raise self.error
        self.frames.append(image)


class EmbeddedCaptureTests(unittest.TestCase):
    def make_loop(self, writer):
        loop = Mainloop.__new__(Mainloop)
        loop.running = True
        loop._sdl_initialized = True
        loop._runtime_thread_id = threading.get_ident()
        loop.multiple_windows = False
        loop._movie_writer = writer
        loop._handle_events = lambda: True
        return loop

    @staticmethod
    def render_two_pixels(renderer, rect, pixel_format, pixels, pitch):
        values = bytes((255, 0, 0, 255, 0, 255, 0, 128))
        ctypes.memmove(pixels, values, len(values))
        return 0

    def test_raw_rgba_capture_reaches_pillow_and_writer_once(self):
        writer = CollectingWriter()
        loop = self.make_loop(writer)

        with patch.object(mainloop_module, "SDL_RenderReadPixels", side_effect=self.render_two_pixels):
            image = loop.update_embedded(FakeCanvas())

        self.assertEqual(image.mode, "RGBA")
        self.assertEqual(image.getpixel((0, 0)), (255, 0, 0, 255))
        self.assertEqual(image.getpixel((1, 0)), (0, 255, 0, 128))
        self.assertEqual(len(writer.frames), 1)
        self.assertIs(writer.frames[0], image)

    def test_encoder_error_is_not_swallowed_by_render_fallback(self):
        writer = CollectingWriter(RuntimeError("broken ffmpeg pipe"))
        loop = self.make_loop(writer)

        with patch.object(mainloop_module, "SDL_RenderReadPixels", side_effect=self.render_two_pixels):
            with self.assertRaisesRegex(RuntimeError, "broken ffmpeg pipe"):
                loop.update_embedded(FakeCanvas())


if __name__ == "__main__":
    unittest.main()
