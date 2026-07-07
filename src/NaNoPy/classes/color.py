from sdl2.ext import Color as Colorsdl2

from NaNoPy.constants._color_data import CSS4_KEYS
from NaNoPy.constants._color_data import CSS4_COLORS

from typing import Optional

import warnings

class _ColorValue:
    """Descriptor that creates a new SDL2 color each time."""

    __slots__ = ("_abgr",)

    def __init__(self, *, r: int, g: int, b: int, a: int) -> None:
        self._abgr = (a, b, g, r)

    def __get__(self, instance, owner):
        return Colorsdl2(*self._abgr)


class Color:
    """Palette helper for NaNoPy shapes.

    Available colors: red, blue, green, yellow, magenta, cyan, white, gray.

    Usage example ``Color.red``.

    For custom colors use ``Color.custom(r=<r>, g=<g>, b=<b>, a=<a>)``. At
    least one channel must be provided; omitted RGB channels default to 0 and
    alpha defaults to 255 so supplying ``g=100`` yields a dark green.
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
    ) -> Colorsdl2:
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
        return Colorsdl2(alpha, blue, green, red)

    @staticmethod
    def css(color_name: CSS4_KEYS) -> Colorsdl2:
        """
        Create a Color object from an CSS4 color name.
        Args:
            color_name (CSS4_COLORS): The name of the CSS4 color to retrieve.
                Must be a valid key from the CSS4_COLORS dictionary.
        Returns:
            Colorsdl2: A Color object initialized from the hexadecimal value
                of the specified CSS4 color. White if not found.
        Example:
            >>> red = Color.css("red")
            >>> blue = Color.css("blanchedalmond")
        """
        
        return Color.hex(CSS4_COLORS.get(color_name, "#ffffff"))

    @staticmethod
    def hex(hex_value: str) -> Colorsdl2:
        """
        Create a Color from a hexadecimal color string.
        Converts a hex color string (with or without '#' prefix) to a Color object.
        If only RGB values are provided (6 characters), alpha is set to 255 (fully opaque).
        Args:
            hex_value (str): A hexadecimal color string in the format '#RRGGBB' or '#RRGGBBAA'.
                            The '#' prefix is optional. Supports both 6-character (RGB) and 
                            8-character (RGBA) hex values.
        Returns:
            Colorsdl2: A Color object with the specified RGBA values.
        Examples:
            >>> color1 = Color.hex("#FF5733")  # RGB with alpha defaulting to 255
            >>> color2 = Color.hex("FF5733FF")  # RGBA without '#' prefix
            >>> color3 = Color.hex("#000000")   # Black with full opacity
        """

        hex_value = hex_value.lstrip("#")

        # Add alpha 255 by default
        if len(hex_value) == 6: hex_value = hex_value + "FF"

        return Color.custom(r=int(hex_value[:2], 16),
                            g=int(hex_value[2:4], 16),
                            b=int(hex_value[4:6], 16),
                            a=int(hex_value[6:8], 16))

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