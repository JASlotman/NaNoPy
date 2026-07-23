import ctypes
import importlib
import os
import threading
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from sdl2 import SDL_CreateRenderer
from sdl2 import SDL_CreateWindow
from sdl2 import SDL_DestroyRenderer
from sdl2 import SDL_DestroyWindow
from sdl2 import SDL_GetError
from sdl2 import SDL_Init
from sdl2 import SDL_INIT_VIDEO
from sdl2 import SDL_PIXELFORMAT_RGBA32
from sdl2 import SDL_QuitSubSystem
from sdl2 import SDL_RENDERER_SOFTWARE
from sdl2 import SDL_RenderClear
from sdl2 import SDL_RenderReadPixels
from sdl2 import SDL_SetRenderDrawColor
from sdl2 import SDL_WasInit
from sdl2 import SDL_WINDOW_HIDDEN

writer_module = importlib.import_module("NaNoPy.classes.writer")
mainloop_module = importlib.import_module("NaNoPy.classes.mainloop")
WriterNaive = writer_module.WriterNaive
Color = writer_module.Color
Mainloop = mainloop_module.Mainloop


class FakeMainloop:
    multiple_windows = False

    def __init__(self):
        self.active = True

    def _canvas_is_active(self, _canvas):
        return self.active


class FakeCanvas:
    def __init__(self, *, width=120, height=100):
        self.window = object()
        self.renderer = object()
        self.name = "coordinate-test"
        self.NNP = FakeMainloop()
        self._reload_fonts = False
        self._size = (width, height)

    def get_window_size(self):
        return self._size


class WriterCoordinateTests(unittest.TestCase):
    def setUp(self):
        self.canvas = FakeCanvas()
        self.writer = WriterNaive(self.canvas, NNP=self.canvas.NNP)
        self.color = object()

    def test_cartesian_y_conversion_includes_last_pixel_row(self):
        self.assertEqual(self.writer._to_sdl_y(0), 99)
        self.assertEqual(self.writer._to_sdl_y(99), 0)
        self.assertEqual(self.writer._to_sdl_y(10.25), 88)

    def test_point_line_rectangle_circle_and_string_share_conversion(self):
        with (
            patch.object(writer_module, "pixelColor") as pixel,
            patch.object(writer_module, "aalineColor") as line,
            patch.object(writer_module, "thickLineColor") as thick_line,
            patch.object(writer_module, "boxColor") as box,
            patch.object(writer_module, "rectangleColor") as rectangle,
            patch.object(writer_module, "filledCircleColor") as filled_circle,
            patch.object(writer_module, "aacircleColor") as circle,
            patch.object(writer_module, "stringColor") as string,
        ):
            self.writer.draw_pixel(1.9, 2.25, self.color)
            self.writer.draw_line(1, 0, 2, 99, self.color)
            self.writer.draw_line_thick(1, 10, 2, 20, 3, self.color)
            self.writer.draw_rectangle(1, 2, 3, 4, self.color, filled=True)
            self.writer.draw_rectangle(1, 2, 3, 4, self.color, filled=False)
            self.writer.draw_circle(5, 50, 2, self.color, filled=True)
            self.writer.draw_circle(5, 50, 2, self.color, filled=False)
            self.writer.draw_string(6, 99, self.color, "test")

        pixel.assert_called_once_with(self.canvas.renderer, 1, 96, self.color)
        line.assert_called_once_with(self.canvas.renderer, 1, 99, 2, 0, self.color)
        thick_line.assert_called_once_with(self.canvas.renderer, 1, 89, 2, 79, 3, self.color)
        box.assert_called_once_with(self.canvas.renderer, 1, 97, 4, 93, self.color)
        rectangle.assert_called_once_with(self.canvas.renderer, 1, 97, 4, 93, self.color)
        filled_circle.assert_called_once_with(self.canvas.renderer, 5, 49, 2, self.color)
        circle.assert_called_once_with(self.canvas.renderer, 5, 49, 2, self.color)
        string.assert_called_once_with(self.canvas.renderer, 6, 0, b"test", self.color)

    def test_custom_polygon_casts_float_points_and_converts_y(self):
        points = [(1.9, 2.25), (5.1, 10.8), (9.9, 20.2)]

        with (
            patch.object(writer_module, "filledPolygonColor") as filled_polygon,
            patch.object(writer_module, "aapolygonColor") as polygon,
        ):
            self.writer.draw_polygon_custom(points, self.color)
            self.writer.draw_polygon_custom(points, self.color, filled=True)

        outline_args = polygon.call_args.args
        self.assertIs(outline_args[0], self.canvas.renderer)
        self.assertEqual(list(outline_args[1]), [1, 5, 9])
        self.assertEqual(list(outline_args[2]), [96, 88, 78])
        self.assertEqual(outline_args[3:], (3, self.color))

        filled_args = filled_polygon.call_args.args
        self.assertEqual(list(filled_args[1]), [1, 5, 9])
        self.assertEqual(list(filled_args[2]), [96, 88, 78])
        self.assertEqual(filled_args[3:], (3, self.color))

    def test_custom_polygon_rejects_fewer_than_three_points(self):
        with patch.object(writer_module, "aapolygonColor") as polygon:
            for points in ([], [(1, 2)], [(1, 2), (3, 4)]):
                with self.subTest(points=points):
                    with self.assertRaisesRegex(ValueError, "at least three points"):
                        self.writer.draw_polygon_custom(points, self.color)

        polygon.assert_not_called()

    def test_drawing_after_window_close_is_a_safe_no_op(self):
        self.canvas.NNP.active = False

        with (
            patch.object(writer_module, "pixelColor") as pixel,
            patch.object(writer_module, "aalineColor") as line,
            patch.object(writer_module, "aapolygonColor") as polygon,
            patch.object(writer_module, "stringColor") as string,
        ):
            self.writer.draw_pixel(1, 2, self.color)
            self.writer.draw_line(1, 2, 3, 4, self.color)
            self.writer.draw_polygon_custom([(0, 0), (1, 0), (0, 1)], self.color)
            self.writer.draw_string(1, 2, self.color, "closed")

        self.assertIsNone(self.writer.window)
        self.assertIsNone(self.writer.renderer)
        pixel.assert_not_called()
        line.assert_not_called()
        polygon.assert_not_called()
        string.assert_not_called()

    def test_regular_polygon_and_star_validate_n_before_building_points(self):
        with patch.object(self.writer, "draw_polygon_custom") as polygon:
            for n in (0, 1, 2):
                with self.subTest(shape="polygon", n=n):
                    with self.assertRaisesRegex(ValueError, "at least three points"):
                        self.writer.draw_polygon(10, 20, 4, n, self.color)

                with self.subTest(shape="star", n=n):
                    with self.assertRaisesRegex(ValueError, "at least three points"):
                        self.writer.draw_star(10, 20, 4, n, self.color)

        polygon.assert_not_called()

    def test_regular_polygon_builds_cartesian_points_then_converts_once(self):
        with patch.object(writer_module, "aapolygonColor") as polygon:
            self.writer.draw_polygon(10, 20, 4, 4, self.color)

        args = polygon.call_args.args
        self.assertEqual(list(args[1]), [10, 14, 10, 6])
        self.assertEqual(list(args[2]), [75, 79, 83, 79])

    def test_star_passes_public_coordinates_to_custom_polygon(self):
        with patch.object(self.writer, "draw_polygon_custom") as polygon:
            self.writer.draw_star(10, 20, 4, 4, self.color, filled=True)

        points, color, filled = polygon.call_args.args
        self.assertEqual(len(points), 8)
        self.assertAlmostEqual(points[0][0], 14)
        self.assertAlmostEqual(points[0][1], 20)
        self.assertTrue(all(16 <= point[1] <= 24 for point in points))
        self.assertIs(color, self.color)
        self.assertTrue(filled)


class WriterSafetyTests(unittest.TestCase):
    def test_cross_thread_drawing_is_rejected_before_sdl_gfx_call(self):
        loop = Mainloop()
        canvas = FakeCanvas()
        canvas.NNP = loop
        writer = WriterNaive(canvas, NNP=loop)
        errors = []

        def draw_from_worker():
            try:
                writer.draw_pixel(1, 2, Color.red)
            except Exception as exc:
                errors.append(exc)

        with (
            patch.object(mainloop_module, "SDL_InitSubSystem", return_value=0),
            patch.object(mainloop_module, "SDL_QuitSubSystem"),
            patch.object(writer_module, "pixelColor") as pixel,
        ):
            loop.ensure_initialized()
            worker = threading.Thread(target=draw_from_worker)
            worker.start()
            worker.join()
            loop.stop()

        self.assertEqual(len(errors), 1)
        self.assertRegex(str(errors[0]), "thread that created")
        pixel.assert_not_called()


class WriterSDLCoordinateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._owns_video_subsystem = not bool(SDL_WasInit(SDL_INIT_VIDEO))
        if cls._owns_video_subsystem and SDL_Init(SDL_INIT_VIDEO) != 0:
            raise RuntimeError(f"SDL video initialization failed: {SDL_GetError()!r}")

        cls.window = SDL_CreateWindow(b"coordinate-test", 0, 0, 1, 3, SDL_WINDOW_HIDDEN)
        if not cls.window:
            if cls._owns_video_subsystem:
                SDL_QuitSubSystem(SDL_INIT_VIDEO)
            raise RuntimeError(f"SDL test window creation failed: {SDL_GetError()!r}")

        cls.renderer = SDL_CreateRenderer(cls.window, -1, SDL_RENDERER_SOFTWARE)
        if not cls.renderer:
            SDL_DestroyWindow(cls.window)
            if cls._owns_video_subsystem:
                SDL_QuitSubSystem(SDL_INIT_VIDEO)
            raise RuntimeError(f"SDL software renderer creation failed: {SDL_GetError()!r}")

        cls.canvas = FakeCanvas(width=1, height=3)
        cls.canvas.window = cls.window
        cls.canvas.renderer = cls.renderer
        cls.writer = WriterNaive(cls.canvas, NNP=cls.canvas.NNP)

    @classmethod
    def tearDownClass(cls):
        SDL_DestroyRenderer(cls.renderer)
        SDL_DestroyWindow(cls.window)
        if cls._owns_video_subsystem:
            SDL_QuitSubSystem(SDL_INIT_VIDEO)

    def read_rows(self):
        pixels = (ctypes.c_ubyte * 12)()
        self.assertEqual(
            SDL_RenderReadPixels(
                self.renderer,
                None,
                SDL_PIXELFORMAT_RGBA32,
                pixels,
                4,
            ),
            0,
        )
        return [tuple(pixels[offset : offset + 4]) for offset in range(0, 12, 4)]

    def test_bottom_and_top_cartesian_pixels_reach_last_and_first_sdl_rows(self):
        self.assertEqual(SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 255), 0)
        self.assertEqual(SDL_RenderClear(self.renderer), 0)
        self.writer.draw_pixel(0, 0, Color.custom(r=17, g=34, b=51))
        self.assertEqual(
            self.read_rows(),
            [(0, 0, 0, 255), (0, 0, 0, 255), (17, 34, 51, 255)],
        )

        self.assertEqual(SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 255), 0)
        self.assertEqual(SDL_RenderClear(self.renderer), 0)
        self.writer.draw_pixel(0, 2, Color.custom(r=51, g=34, b=17))
        self.assertEqual(
            self.read_rows(),
            [(51, 34, 17, 255), (0, 0, 0, 255), (0, 0, 0, 255)],
        )


if __name__ == "__main__":
    unittest.main()
