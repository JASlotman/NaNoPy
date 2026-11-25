"""RGBA frames captured from a canvas, plus the small PNG encoder that displays them.

Frames are plain numpy arrays underneath, so embedded rendering and video
recording need no imaging library. PNG output exists for notebook display and
``Frame.save``; its zlib level trades encode time against file size.
"""

from __future__ import annotations

import struct
import zlib
from operator import index as operator_index
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO, SupportsIndex

import numpy as np

from NaNoPy.constants import DEFAULT_PNG_LEVEL, PNG_LEVEL_MAX, PNG_LEVEL_MIN

if TYPE_CHECKING:
    import ctypes

    from numpy.typing import NDArray

_CHANNELS = 4  # RGBA
_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_PNG_BIT_DEPTH = 8
_PNG_COLOR_TYPE_RGBA = 6
_PNG_FILTER_NONE = 0


def validate_png_level(level: SupportsIndex | None) -> int:
    """Return a usable zlib compression level; ``None`` selects ``DEFAULT_PNG_LEVEL``.

    Any integer-like value is accepted (``int``, numpy integers), but not ``bool``.
    """
    if level is None:
        return DEFAULT_PNG_LEVEL
    if isinstance(level, bool):
        raise TypeError("png_level must be an integer")
    try:
        validated = operator_index(level)
    except TypeError as exc:
        raise TypeError("png_level must be an integer") from exc
    if not PNG_LEVEL_MIN <= validated <= PNG_LEVEL_MAX:
        raise ValueError(f"png_level must be between {PNG_LEVEL_MIN} and {PNG_LEVEL_MAX}")
    return validated


def _png_chunk(tag: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(data, zlib.crc32(tag))
    return b"".join((struct.pack(">I", len(data)), tag, data, struct.pack(">I", crc)))


def _encode_png(pixels: NDArray[np.uint8], level: int) -> bytes:
    """Encode an RGBA8 array as a PNG, leaving every scanline unfiltered.

    Skipping PNG's per-row filters keeps encoding fast and puts the whole
    speed/size trade-off in the zlib level.
    """
    height, width, _ = pixels.shape
    if width == 0 or height == 0:
        raise ValueError("An empty frame cannot be encoded as PNG")

    scanlines = np.empty((height, width * _CHANNELS + 1), dtype=np.uint8)
    scanlines[:, 0] = _PNG_FILTER_NONE
    scanlines[:, 1:] = pixels.reshape(height, width * _CHANNELS)

    header = struct.pack(">IIBBBBB", width, height, _PNG_BIT_DEPTH, _PNG_COLOR_TYPE_RGBA, 0, 0, 0)
    return b"".join(
        (
            _PNG_SIGNATURE,
            _png_chunk(b"IHDR", header),
            _png_chunk(b"IDAT", zlib.compress(memoryview(scanlines), level)),
            _png_chunk(b"IEND", b""),
        ),
    )


class Frame:
    """A read-only RGBA image captured from a canvas.

    Frames are what ``Canvas.update_embedded()`` returns, what ``MovieWriter.add_frame()``
    consumes, and what Jupyter displays as a PNG.

    Args:
        pixels: A ``uint8`` array of shape ``(height, width, 4)`` in RGBA order. The frame
            shares this memory instead of copying it, so do not modify the array afterwards.
        png_level: zlib level (0-9) used when the frame is shown in a notebook. Lower is
            faster to encode, higher gives smaller output. ``None`` uses ``DEFAULT_PNG_LEVEL``.
            See the ``PNG_LEVEL_*`` constants in ``NaNoPy.constants``.

    """

    mode = "RGBA"

    def __init__(self, pixels: NDArray[np.uint8], *, png_level: int | None = None) -> None:
        if not isinstance(pixels, np.ndarray):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError("Frame pixels must be a numpy array")
        if pixels.dtype != np.uint8 or pixels.ndim != 3 or pixels.shape[2] != _CHANNELS:
            raise ValueError("Frame pixels must be a uint8 array of shape (height, width, 4)")

        view = np.ascontiguousarray(pixels).view()
        view.flags.writeable = False
        self._pixels: NDArray[np.uint8] = view
        self._png_level = validate_png_level(png_level)

    @classmethod
    def from_buffer(
        cls,
        data: bytes | bytearray | memoryview | ctypes.Array[ctypes.c_ubyte],
        width: int,
        height: int,
        *,
        png_level: int | None = None,
    ) -> Frame:
        """Wrap tightly packed RGBA bytes without copying them."""
        flat = np.frombuffer(data, dtype=np.uint8)
        expected = width * height * _CHANNELS
        if flat.size != expected:
            raise ValueError(f"Expected {expected} bytes for a {width}x{height} RGBA frame, got {flat.size}")
        return cls(flat.reshape(height, width, _CHANNELS), png_level=png_level)

    @classmethod
    def black(cls, width: int, height: int, *, png_level: int | None = None) -> Frame:
        """Return an opaque black frame."""
        pixels = np.zeros((height, width, _CHANNELS), dtype=np.uint8)
        pixels[..., 3] = 255
        return cls(pixels, png_level=png_level)

    @property
    def width(self) -> int:
        return int(self._pixels.shape[1])

    @property
    def height(self) -> int:
        return int(self._pixels.shape[0])

    @property
    def size(self) -> tuple[int, int]:
        """The frame size as ``(width, height)``."""
        return (self.width, self.height)

    @property
    def array(self) -> NDArray[np.uint8]:
        """The pixels as a read-only ``(height, width, 4)`` RGBA array."""
        return self._pixels

    @property
    def png_level(self) -> int:
        """The zlib level used when this frame is displayed as a PNG."""
        return self._png_level

    @png_level.setter
    def png_level(self, level: int | None) -> None:
        self._png_level = validate_png_level(level)

    def getpixel(self, xy: tuple[int, int]) -> tuple[int, int, int, int]:
        """Return the ``(r, g, b, a)`` value at ``(x, y)``."""
        x, y = xy
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError("pixel coordinates are outside the frame")
        red, green, blue, alpha = (int(value) for value in self._pixels[y, x])
        return (red, green, blue, alpha)

    def tobytes(self) -> bytes:
        """Return the pixels as tightly packed RGBA bytes."""
        return self._pixels.tobytes()

    def to_png(self, level: int | None = None) -> bytes:
        """Encode the frame as PNG.

        Args:
            level: zlib level (0-9) for this call. ``None`` uses the frame's own ``png_level``.

        """
        return _encode_png(self._pixels, self._png_level if level is None else validate_png_level(level))

    def save(self, target: str | PathLike[str] | BinaryIO, *, level: int | None = None) -> None:
        """Write the frame as a PNG to a ``.png`` path or an open binary file."""
        if isinstance(target, str | PathLike):
            path = Path(target)
            if path.suffix.lower() != ".png":
                raise ValueError("Frame.save only writes PNG files; use a .png file name")
            path.write_bytes(self.to_png(level))
        else:
            target.write(self.to_png(level))

    def _repr_png_(self) -> bytes:
        """Let Jupyter and IPython display the frame inline."""
        return self.to_png()

    def __repr__(self) -> str:
        return f"Frame(size={self.size}, mode={self.mode!r}, png_level={self._png_level})"
