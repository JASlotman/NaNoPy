from __future__ import annotations

from sdl2.ext import Color as Colorsdl2

from NaNoPy.constants._color_data import CSS4_KEYS
from NaNoPy.constants._color_data import CSS4_COLORS

from typing import Optional

import sys
import warnings


class _ColorValue:
    """Descriptor that creates a new SDL2 color each time."""

    __slots__ = ("_rgba",)

    def __init__(self, *, r: int, g: int, b: int, a: int) -> None:
        self._rgba = (r, g, b, a)

    def __get__(self, instance, owner) -> Color:
        return Color._from_rgba(*self._rgba)


class Color(Colorsdl2):
    """Palette helper for NaNoPy shapes.

    Available colors: red, blue, green, yellow, magenta, cyan, white, gray.

    Usage example ``Color.red``.

    For custom colors use ``Color.custom(r=<r>, g=<g>, b=<b>, a=<a>)``. At
    least one channel must be provided; omitted RGB channels default to 0 and
    alpha defaults to 255 so supplying ``g=100`` yields a dark green.

    The public properties, iteration order and representation all use the
    conventional ``(red, green, blue, alpha)`` channel order. Integer
    conversion is deliberately different: SDL_gfx's packed-color functions
    consume a native ``Uint32`` whose bytes are ordered ``R, G, B, A``. Its
    numeric form is therefore ``0xAABBGGRR`` on little-endian systems and
    ``0xRRGGBBAA`` on big-endian systems. Keeping this conversion at the SDL
    boundary lets a color remain normal RGBA everywhere else while still
    rendering correctly.
    Copying and the arithmetic operators supported by PySDL2 also return
    immutable NaNoPy colors, preserving that packing behavior.
    """

    red = _ColorValue(r=255, g=0, b=0, a=255)
    blue = _ColorValue(r=0, g=0, b=255, a=255)
    green = _ColorValue(r=0, g=255, b=0, a=255)
    yellow = _ColorValue(r=255, g=255, b=0, a=255)
    magenta = _ColorValue(r=255, g=0, b=255, a=255)
    cyan = _ColorValue(r=0, g=255, b=255, a=255)
    white = _ColorValue(r=255, g=255, b=255, a=255)
    gray = _ColorValue(r=155, g=155, b=155, a=255)
    black = _ColorValue(r=0, g=0, b=0, a=255)
    purple = _ColorValue(r=200, g=0, b=255, a=255)
    orange = _ColorValue(r=240, g=140, b=0, a=255)
    tangerine = _ColorValue(r=230, g=90, b=0, a=255)
    lime = _ColorValue(r=180, g=255, b=0, a=255)
    brown = _ColorValue(r=100, g=50, b=0, a=255)

    @classmethod
    def _from_rgba(cls, r: int, g: int, b: int, a: int) -> Color:
        """Construct a frozen ``Color`` directly, bypassing the deprecated public constructor."""

        self = object.__new__(cls)
        for name, val in (("_r", r), ("_g", g), ("_b", b), ("_a", a)):
            Colorsdl2._verify_rgba_value(self, val)
            object.__setattr__(self, name, float(int(val)))
        return self

    def __setattr__(self, name, value) -> None:
        raise AttributeError(f"{type(self).__name__} is immutable")

    def __delattr__(self, name) -> None:
        raise AttributeError(f"{type(self).__name__} is immutable")

    def __hash__(self) -> int:
        return hash((self.r, self.g, self.b, self.a))

    def _as_sdl_gfx_uint32(self) -> int:
        """Pack this RGBA color in the integer layout consumed by SDL_gfx.

        SDL_gfx reads the native in-memory bytes of its ``Uint32`` color
        argument as red, green, blue and alpha. :meth:`int.from_bytes` makes
        that byte-level contract explicit and gives the correct numeric value
        on either host byte order. PySDL2's base ``Color`` always returns
        ``0xRRGGBBAA``, which swaps channels when passed through ctypes on a
        little-endian host.
        """

        rgba_bytes = bytes((self.r, self.g, self.b, self.a))
        return int.from_bytes(rgba_bytes, byteorder=sys.byteorder)

    def __int__(self) -> int:
        return self._as_sdl_gfx_uint32()

    def __index__(self) -> int:
        return self._as_sdl_gfx_uint32()

    def __float__(self) -> float:
        return float(self._as_sdl_gfx_uint32())

    def __long__(self) -> int:
        """Return the native SDL_gfx value for PySDL2 API compatibility."""

        return self._as_sdl_gfx_uint32()

    def __hex__(self) -> str:
        """Return the native SDL_gfx value in hexadecimal form."""

        return hex(self._as_sdl_gfx_uint32())

    def __oct__(self) -> str:
        """Return the native SDL_gfx value in octal form."""

        return oct(self._as_sdl_gfx_uint32())

    def __copy__(self) -> Color:
        """Return this immutable value without losing NaNoPy's packing hooks."""

        return self

    def __deepcopy__(self, memo) -> Color:
        """Return this immutable value without losing NaNoPy's packing hooks."""

        return self

    def __invert__(self) -> Color:
        return Color._from_rgba(
            255 - self.r,
            255 - self.g,
            255 - self.b,
            255 - self.a,
        )

    def __mod__(self, color: Colorsdl2) -> Color:
        return Color._from_rgba(
            self.r % color.r,
            self.g % color.g,
            self.b % color.b,
            self.a % color.a,
        )

    def __truediv__(self, color: Colorsdl2) -> Color:
        channels = []
        for own_value, other_value in zip(
            (self._r, self._g, self._b, self._a),
            (color._r, color._g, color._b, color._a),
            strict=True,
        ):
            channels.append(0 if other_value == 0 else own_value / other_value)
        return Color._from_rgba(*channels)

    def __div__(self, color: Colorsdl2) -> Color:
        """Compatibility alias matching PySDL2's legacy division hook."""

        return self.__truediv__(color)

    def __mul__(self, color: Colorsdl2) -> Color:
        return Color._from_rgba(
            min(self._r * color._r, 255),
            min(self._g * color._g, 255),
            min(self._b * color._b, 255),
            min(self._a * color._a, 255),
        )

    def __sub__(self, color: Colorsdl2) -> Color:
        return Color._from_rgba(
            max(self.r - color.r, 0),
            max(self.g - color.g, 0),
            max(self.b - color.b, 0),
            max(self.a - color.a, 0),
        )

    def __add__(self, color: Colorsdl2) -> Color:
        return Color._from_rgba(
            min(self.r + color.r, 255),
            min(self.g + color.g, 255),
            min(self.b + color.b, 255),
            min(self.a + color.a, 255),
        )

    def __init__(self) -> None:
        warnings.warn(
            "Instantiating Color is deprecated; access colors directly via"
            " class attributes (e.g. Color.red).",
            DeprecationWarning,
            stacklevel=2,
        )

    @staticmethod
    def custom(
        *,
        r: Optional[int] = None,
        g: Optional[int] = None,
        b: Optional[int] = None,
        a: Optional[int] = None,
    ) -> Color:
        """Return a custom SDL2 color with sane defaults.

        At least one RGB channel must be provided. Missing RGB channels default
        to 0 and alpha defaults to 255.
        """

        if r is None and g is None and b is None:
            raise ValueError("Provide at least one of r, g or b when requesting a custom color.")

        red = 0 if r is None else r
        green = 0 if g is None else g
        blue = 0 if b is None else b
        alpha = 255 if a is None else a
        return Color._from_rgba(red, green, blue, alpha)

    @staticmethod
    def css(color_name: CSS4_KEYS) -> Color:
        """
        Create a Color object from an CSS4 color name.
        Args:
            color_name (CSS4_COLORS): The name of the CSS4 color to retrieve.
                Must be a valid key from the CSS4_COLORS dictionary.
        Returns:
            Color: A Color object initialized from the hexadecimal value
                of the specified CSS4 color. White if not found.
        Example:
            >>> red = Color.css("red")
            >>> blue = Color.css("blanchedalmond")
        """

        return Color.hex(CSS4_COLORS.get(color_name, "#ffffff"))

    @staticmethod
    def hex(hex_value: str) -> Color:
        """
        Create a Color from a hexadecimal color string.
        Converts a hex color string (with or without '#' prefix) to a Color object.
        If only RGB values are provided (6 characters), alpha is set to 255 (fully opaque).
        Args:
            hex_value (str): A hexadecimal color string in the format '#RRGGBB' or '#RRGGBBAA'.
                            The '#' prefix is optional. Supports both 6-character (RGB) and
                            8-character (RGBA) hex values.
        Returns:
            Color: A Color object with the specified RGBA values.
        Examples:
            >>> color1 = Color.hex("#FF5733")  # RGB with alpha defaulting to 255
            >>> color2 = Color.hex("FF5733FF")  # RGBA without '#' prefix
            >>> color3 = Color.hex("#000000")   # Black with full opacity
        """

        hex_value = hex_value.lstrip("#")

        # Add alpha 255 by default
        if len(hex_value) == 6:
            hex_value += "FF"

        return Color.custom(
            r=int(hex_value[:2], 16),
            g=int(hex_value[2:4], 16),
            b=int(hex_value[4:6], 16),
            a=int(hex_value[6:8], 16),
        )

    def __call__(
        self,
        *,
        r: Optional[int] = None,
        g: Optional[int] = None,
        b: Optional[int] = None,
        a: Optional[int] = None,
    ) -> Colorsdl2:
        warnings.warn(
            "Calling Color instances is deprecated; use Color.custom(...) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.custom(r=r, g=g, b=b, a=a)
