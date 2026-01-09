import warnings
from typing import Optional
from sdl2.ext import Color as Colorsdl2


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

        At least onrge RGB channel must be provided. Missing RGB channels default
        to 0 and alpha defaults to 255.
        """

        if r is None and g is None and b is None:
            raise ValueError("Provide at least one of r, g or b when requesting a custom color.")

        red = 0 if r is None else r
        green = 0 if g is None else g
        blue = 0 if b is None else b
        alpha = 255 if a is None else a
        return Colorsdl2(alpha, blue, green, red)

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
