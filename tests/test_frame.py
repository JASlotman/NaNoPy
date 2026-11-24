"""Tests for the numpy-backed Frame and its PNG encoder."""

import base64
import importlib.util
import io
import os
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from typing import Any

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import numpy as np

from NaNoPy.classes.frame import Frame, validate_png_level
from NaNoPy.constants import (
    DEFAULT_PNG_LEVEL,
    PNG_LEVEL_BALANCED,
    PNG_LEVEL_FAST,
    PNG_LEVEL_MAX,
    PNG_LEVEL_MIN,
    PNG_LEVEL_SMALL,
)

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def striped_frame(width: int = 64, height: int = 48, **kwargs: int | None) -> Frame:
    """A compressible frame, like a typical drawing: flat background plus stripes."""
    pixels = np.zeros((height, width, 4), dtype=np.uint8)
    pixels[..., 3] = 255
    pixels[::4, :, 0] = 200
    pixels[:, ::5, 2] = 90
    return Frame(pixels, **kwargs)


class FrameTests(unittest.TestCase):
    def decode_png(self, data: bytes) -> tuple[int, int, bytes]:
        """Read a PNG without any imaging library, checking structure and CRCs."""
        self.assertEqual(data[:8], PNG_SIGNATURE)
        position = 8
        chunks: list[tuple[bytes, bytes]] = []
        while position < len(data):
            length, tag = struct.unpack(">I4s", data[position : position + 8])
            body = data[position + 8 : position + 8 + length]
            (crc,) = struct.unpack(">I", data[position + 8 + length : position + 12 + length])
            self.assertEqual(crc, zlib.crc32(tag + body), f"bad CRC in {tag!r}")
            chunks.append((tag, body))
            position += 12 + length
        self.assertEqual(position, len(data))
        self.assertEqual([tag for tag, _ in chunks], [b"IHDR", b"IDAT", b"IEND"])

        width, height, *fields = struct.unpack(">IIBBBBB", chunks[0][1])
        self.assertEqual(fields, [8, 6, 0, 0, 0])  # 8-bit RGBA, no interlace
        raw = zlib.decompress(chunks[1][1])
        stride = width * 4 + 1
        self.assertEqual(len(raw), stride * height)
        pixels = bytearray()
        for row in range(height):
            line = raw[row * stride : (row + 1) * stride]
            self.assertEqual(line[0], 0, "encoder must use PNG filter type 0")
            pixels += line[1:]
        return width, height, bytes(pixels)

    # --- construction and pixel access -------------------------------------------------

    def test_from_buffer_wraps_rgba_bytes(self) -> None:
        data = bytes((255, 0, 0, 255, 0, 255, 0, 128))
        frame = Frame.from_buffer(data, 2, 1)

        self.assertEqual(frame.size, (2, 1))
        self.assertEqual((frame.width, frame.height), (2, 1))
        self.assertEqual(frame.mode, "RGBA")
        self.assertEqual(frame.getpixel((0, 0)), (255, 0, 0, 255))
        self.assertEqual(frame.getpixel((1, 0)), (0, 255, 0, 128))
        self.assertEqual(frame.tobytes(), data)
        self.assertEqual(frame.array.shape, (1, 2, 4))
        self.assertTrue(np.shares_memory(frame.array, np.frombuffer(data, dtype=np.uint8)))

    def test_pixels_are_read_only(self) -> None:
        frame = Frame.black(2, 2)
        with self.assertRaises(ValueError):
            frame.array[0, 0, 0] = 1

    def test_from_buffer_rejects_wrong_length(self) -> None:
        with self.assertRaisesRegex(ValueError, "Expected 8 bytes"):
            Frame.from_buffer(bytes(7), 2, 1)

    def test_constructor_validates_the_pixel_array(self) -> None:
        with self.assertRaises(TypeError):
            Frame(b"not an array")  # type: ignore[arg-type]
        # Deliberately wrong inputs, so they are typed as Any rather than as uint8 arrays.
        invalid_pixels: dict[str, Any] = {
            "float dtype": np.zeros((2, 2, 4), dtype=np.float32),
            "two dimensions": np.zeros((2, 8), dtype=np.uint8),
            "RGB, not RGBA": np.zeros((2, 2, 3), dtype=np.uint8),
        }
        for label, pixels in invalid_pixels.items():
            with self.subTest(label), self.assertRaisesRegex(ValueError, "uint8 array of shape"):
                Frame(pixels)

    def test_non_contiguous_arrays_are_accepted(self) -> None:
        wide = np.zeros((2, 6, 4), dtype=np.uint8)
        wide[..., 3] = 255
        frame = Frame(wide[:, ::2])  # a strided view
        self.assertEqual(frame.size, (3, 2))
        self.assertEqual(len(frame.tobytes()), 3 * 2 * 4)

    def test_black_frame_is_opaque(self) -> None:
        frame = Frame.black(3, 2)
        self.assertEqual(frame.size, (3, 2))
        self.assertEqual(frame.getpixel((2, 1)), (0, 0, 0, 255))

    def test_getpixel_rejects_coordinates_outside_the_frame(self) -> None:
        frame = Frame.black(2, 1)
        for coordinates in ((2, 0), (0, 1), (-1, 0), (0, -1)):
            with self.subTest(coordinates), self.assertRaises(IndexError):
                frame.getpixel(coordinates)

    def test_empty_frame_exists_but_cannot_become_a_png(self) -> None:
        frame = Frame.black(0, 5)
        self.assertEqual(frame.size, (0, 5))
        with self.assertRaisesRegex(ValueError, "empty frame"):
            frame.to_png()

    # --- compression level -------------------------------------------------------------

    def test_presets_form_a_valid_range_and_default_is_the_fast_one(self) -> None:
        self.assertEqual(DEFAULT_PNG_LEVEL, PNG_LEVEL_FAST)
        self.assertLess(PNG_LEVEL_FAST, PNG_LEVEL_BALANCED)
        self.assertLess(PNG_LEVEL_BALANCED, PNG_LEVEL_SMALL)
        for level in (PNG_LEVEL_MIN, PNG_LEVEL_FAST, PNG_LEVEL_BALANCED, PNG_LEVEL_SMALL, PNG_LEVEL_MAX):
            self.assertEqual(validate_png_level(level), level)

    def test_validate_png_level(self) -> None:
        self.assertEqual(validate_png_level(None), DEFAULT_PNG_LEVEL)
        self.assertEqual(validate_png_level(np.int64(3)), 3)
        for bad in (True, 1.5, "1", [1]):
            with self.subTest(bad), self.assertRaisesRegex(TypeError, "png_level must be an integer"):
                validate_png_level(bad)  # type: ignore[arg-type]
        for out_of_range in (PNG_LEVEL_MIN - 1, PNG_LEVEL_MAX + 1):
            with self.subTest(out_of_range), self.assertRaisesRegex(ValueError, "png_level must be between"):
                validate_png_level(out_of_range)

    def test_constructor_and_call_reject_invalid_levels(self) -> None:
        frame = Frame.black(1, 1)
        with self.assertRaises(ValueError):
            Frame.black(1, 1, png_level=10)
        with self.assertRaises(ValueError):
            frame.to_png(level=-1)

    def test_png_level_property_validates_and_none_restores_the_default(self) -> None:
        frame = Frame.black(1, 1, png_level=PNG_LEVEL_SMALL)
        self.assertEqual(frame.png_level, PNG_LEVEL_SMALL)

        frame.png_level = None
        self.assertEqual(frame.png_level, DEFAULT_PNG_LEVEL)

        frame.png_level = PNG_LEVEL_MIN
        with self.assertRaises(ValueError):
            frame.png_level = 99
        self.assertEqual(frame.png_level, PNG_LEVEL_MIN, "a rejected level must not change the frame")

    # --- PNG output --------------------------------------------------------------------

    def test_png_round_trips_at_every_level(self) -> None:
        rng = np.random.default_rng(1234)
        noisy = Frame(rng.integers(0, 256, (5, 7, 4), dtype=np.uint8))
        for frame in (noisy, striped_frame()):
            for level in range(PNG_LEVEL_MIN, PNG_LEVEL_MAX + 1):
                with self.subTest(size=frame.size, level=level):
                    width, height, pixels = self.decode_png(frame.to_png(level))
                    self.assertEqual(frame.size, (width, height))
                    self.assertEqual(pixels, frame.tobytes())

    def test_level_trades_size_for_effort(self) -> None:
        frame = striped_frame(256, 192)
        stored = frame.to_png(PNG_LEVEL_MIN)
        fast = frame.to_png(PNG_LEVEL_FAST)
        small = frame.to_png(PNG_LEVEL_SMALL)

        self.assertGreater(len(stored), len(fast), "level 0 stores the data uncompressed")
        self.assertGreater(len(stored), len(small))
        self.assertNotEqual(fast, small)

    def test_call_level_overrides_the_frame_level_and_none_uses_it(self) -> None:
        frame = striped_frame(png_level=PNG_LEVEL_MIN)
        self.assertEqual(frame.to_png(), frame.to_png(PNG_LEVEL_MIN))
        self.assertEqual(frame.to_png(PNG_LEVEL_SMALL), striped_frame(png_level=PNG_LEVEL_SMALL).to_png())
        self.assertEqual(frame.png_level, PNG_LEVEL_MIN, "a per-call level must not stick to the frame")

    def test_repr_png_uses_the_frame_level(self) -> None:
        frame = striped_frame()
        self.assertEqual(frame._repr_png_(), frame.to_png(DEFAULT_PNG_LEVEL))

        frame.png_level = PNG_LEVEL_MIN
        self.assertEqual(frame._repr_png_(), frame.to_png(PNG_LEVEL_MIN))
        self.assertNotEqual(frame._repr_png_(), frame.to_png(PNG_LEVEL_SMALL))

    def test_save_writes_a_png_to_a_path_or_a_file_object(self) -> None:
        frame = striped_frame()
        with tempfile.TemporaryDirectory() as directory:
            as_path = Path(directory, "frame.PNG")
            frame.save(as_path, level=PNG_LEVEL_SMALL)
            self.assertEqual(as_path.read_bytes(), frame.to_png(PNG_LEVEL_SMALL))

            as_text = str(Path(directory, "again.png"))
            frame.save(as_text)
            self.assertEqual(Path(as_text).read_bytes(), frame.to_png())

            wrong_suffix = Path(directory, "frame.jpg")
            with self.assertRaisesRegex(ValueError, "only writes PNG"):
                frame.save(wrong_suffix)
            self.assertFalse(wrong_suffix.exists())

        buffer = io.BytesIO()
        frame.save(buffer, level=PNG_LEVEL_MIN)
        self.assertEqual(buffer.getvalue(), frame.to_png(PNG_LEVEL_MIN))

    def test_repr_describes_the_frame(self) -> None:
        self.assertEqual(repr(Frame.black(3, 2, png_level=6)), "Frame(size=(3, 2), mode='RGBA', png_level=6)")

    # --- integration -------------------------------------------------------------------

    @unittest.skipUnless(importlib.util.find_spec("IPython"), "IPython (the 'interactive' extra) is not installed")
    def test_ipython_displays_a_frame_as_png_at_its_level(self) -> None:
        from IPython.core.formatters import DisplayFormatter  # noqa: PLC0415 - optional dependency

        frame = striped_frame(png_level=PNG_LEVEL_MIN)
        bundle, _ = DisplayFormatter().format(frame)

        png = bundle["image/png"]
        if isinstance(png, str):  # some IPython versions return base64 text
            png = base64.b64decode(png)
        self.assertEqual(png, frame.to_png(PNG_LEVEL_MIN))
        self.assertEqual(self.decode_png(png)[2], frame.tobytes())

    def test_package_imports_and_encodes_without_pillow(self) -> None:
        """Regression guard: Pillow must not creep back in as a hard dependency."""
        script = (
            "import sys\n"
            "sys.modules['PIL'] = None  # makes any `import PIL` raise ImportError\n"
            "import NaNoPy, NaNoPy.decorators\n"
            "from NaNoPy import Frame\n"
            "assert Frame.black(2, 2).to_png().startswith(b'\\x89PNG')\n"
        )
        result = subprocess.run(  # noqa: S603 - fixed interpreter and script
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
