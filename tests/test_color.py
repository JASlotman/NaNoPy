import copy
import ctypes
import importlib
import operator
import os
import sys
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
from sdl2.sdlgfx import pixelColor

from NaNoPy.classes.color import Color

color_module = importlib.import_module("NaNoPy.classes.color")


class ColorSemanticsTests(unittest.TestCase):
    def assert_rgba(self, color, expected):
        self.assertEqual((color.r, color.g, color.b, color.a), expected)
        self.assertEqual(tuple(color), expected)
        self.assertEqual(tuple(color[index] for index in range(4)), expected)

    def test_named_colors_expose_channels_in_rgba_order(self):
        expected_colors = {
            "red": (255, 0, 0, 255),
            "blue": (0, 0, 255, 255),
            "green": (0, 255, 0, 255),
            "yellow": (255, 255, 0, 255),
            "magenta": (255, 0, 255, 255),
            "cyan": (0, 255, 255, 255),
            "white": (255, 255, 255, 255),
            "gray": (155, 155, 155, 255),
            "black": (0, 0, 0, 255),
            "purple": (200, 0, 255, 255),
            "orange": (240, 140, 0, 255),
            "tangerine": (230, 90, 0, 255),
            "lime": (180, 255, 0, 255),
            "brown": (100, 50, 0, 255),
        }

        for name, expected in expected_colors.items():
            with self.subTest(name=name):
                self.assert_rgba(getattr(Color, name), expected)

    def test_custom_factory_preserves_full_and_defaulted_rgba_values(self):
        full = Color.custom(r=1, g=2, b=3, a=4)
        defaulted = Color.custom(g=17)

        self.assert_rgba(full, (1, 2, 3, 4))
        self.assertEqual(repr(full), "Color(r=1, g=2, b=3, a=4)")
        self.assert_rgba(defaulted, (0, 17, 0, 255))

    def test_css_factory_preserves_rgba_values(self):
        self.assert_rgba(Color.css("rebeccapurple"), (102, 51, 153, 255))
        self.assert_rgba(Color.css("not-a-css-color"), (255, 255, 255, 255))

    def test_hex_factory_preserves_rgb_and_optional_alpha(self):
        self.assert_rgba(Color.hex("#123456"), (18, 52, 86, 255))
        self.assert_rgba(Color.hex("12345678"), (18, 52, 86, 120))

    def test_integer_protocol_uses_native_rgba_byte_packing(self):
        color = Color.custom(r=0x11, g=0x22, b=0x33, a=0x44)
        expected = int.from_bytes(bytes((0x11, 0x22, 0x33, 0x44)), sys.byteorder)
        native_value = ctypes.c_uint32(color)

        self.assertEqual(int(color), expected)
        self.assertEqual(operator.index(color), expected)
        self.assertEqual(native_value.value, expected)
        self.assertEqual(
            ctypes.string_at(ctypes.byref(native_value), ctypes.sizeof(native_value)),
            bytes((0x11, 0x22, 0x33, 0x44)),
        )
        self.assertEqual(float(color), float(expected))
        self.assertEqual(hex(color), hex(expected))
        self.assertEqual(oct(color), oct(expected))
        self.assertEqual(color.__long__(), expected)
        self.assertEqual(color.__hex__(), hex(expected))
        self.assertEqual(color.__oct__(), oct(expected))

    def test_integer_packing_adapts_to_both_host_byte_orders(self):
        color = Color.custom(r=0x11, g=0x22, b=0x33, a=0x44)

        for byteorder, expected in (("little", 0x44332211), ("big", 0x11223344)):
            with self.subTest(byteorder=byteorder):
                with patch.object(color_module.sys, "byteorder", byteorder):
                    self.assertEqual(int(color), expected)
                    self.assertEqual(operator.index(color), expected)
                    self.assertEqual(color.__long__(), expected)
                    self.assertEqual(color.__hex__(), hex(expected))
                    self.assertEqual(color.__oct__(), oct(expected))

    def test_arithmetic_keeps_immutable_nanopy_colors_and_native_packing(self):
        left = Color.custom(r=10, g=20, b=30, a=40)
        right = Color.custom(r=3, g=6, b=7, a=9)
        operations = {
            "invert": (~left, (245, 235, 225, 215)),
            "add": (left + right, (13, 26, 37, 49)),
            "subtract": (left - right, (7, 14, 23, 31)),
            "multiply": (left * right, (30, 120, 210, 255)),
            "divide": (left / right, (3, 3, 4, 4)),
            "legacy-divide": (left.__div__(right), (3, 3, 4, 4)),
            "modulo": (left % right, (1, 2, 2, 4)),
        }

        for name, (result, expected) in operations.items():
            with self.subTest(name=name):
                self.assertIs(type(result), Color)
                self.assert_rgba(result, expected)
                packed = int.from_bytes(bytes(expected), sys.byteorder)
                self.assertEqual(int(result), packed)
                with self.assertRaisesRegex(AttributeError, "immutable"):
                    result.r = 0

    def test_copying_an_immutable_color_preserves_nanopy_type_and_packing(self):
        color = Color.custom(r=10, g=20, b=30, a=40)

        self.assertIs(copy.copy(color), color)
        self.assertIs(copy.deepcopy(color), color)
        self.assertEqual(int(copy.copy(color)), int.from_bytes(bytes((10, 20, 30, 40)), sys.byteorder))


class ColorSDLRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.owns_video_subsystem = SDL_WasInit(SDL_INIT_VIDEO) == 0
        if cls.owns_video_subsystem and SDL_Init(SDL_INIT_VIDEO) != 0:
            raise RuntimeError(f"SDL video initialization failed: {SDL_GetError()!r}")

        cls.window = SDL_CreateWindow(b"color-test", 0, 0, 1, 1, SDL_WINDOW_HIDDEN)
        if not cls.window:
            if cls.owns_video_subsystem:
                SDL_QuitSubSystem(SDL_INIT_VIDEO)
            raise RuntimeError(f"SDL test window creation failed: {SDL_GetError()!r}")

        cls.renderer = SDL_CreateRenderer(cls.window, -1, SDL_RENDERER_SOFTWARE)
        if not cls.renderer:
            SDL_DestroyWindow(cls.window)
            if cls.owns_video_subsystem:
                SDL_QuitSubSystem(SDL_INIT_VIDEO)
            raise RuntimeError(f"SDL software renderer creation failed: {SDL_GetError()!r}")

    @classmethod
    def tearDownClass(cls):
        SDL_DestroyRenderer(cls.renderer)
        SDL_DestroyWindow(cls.window)
        if cls.owns_video_subsystem:
            SDL_QuitSubSystem(SDL_INIT_VIDEO)

    def test_packed_color_reaches_sdl_gfx_without_channel_swapping(self):
        color = Color.custom(r=17, g=34, b=51, a=255)

        self.assertEqual(SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 255), 0)
        self.assertEqual(SDL_RenderClear(self.renderer), 0)
        self.assertEqual(pixelColor(self.renderer, 0, 0, color), 0)

        pixels = (ctypes.c_ubyte * 4)()
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
        self.assertEqual(tuple(pixels), (17, 34, 51, 255))


if __name__ == "__main__":
    unittest.main()
