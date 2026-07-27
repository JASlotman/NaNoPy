import ctypes
import math
import warnings
from collections.abc import Callable, Iterable, Sequence
from typing import cast

from sdl2.sdlgfx import (
    aacircleColor,
    aalineColor,
    aapolygonColor,
    boxColor,
    filledCircleColor,
    filledPolygonColor,
    gfxPrimitivesSetFont,
    pixelColor,
    rectangleColor,
    stringColor,
    thickLineColor,
)

from NaNoPy.classes.canvas import CanvasNaive
from NaNoPy.classes.color import Color
from NaNoPy.classes.mainloop import Mainloop
from NaNoPy.classes.spline import Spline

_LEGACY_DRAW_METHODS = {
    "drawCircle": "draw_circle",
    "drawLine": "draw_line",
    "drawPixel": "draw_pixel",
    "drawPolygon": "draw_polygon",
    "drawRectangle": "draw_rectangle",
    "drawSpline": "draw_spline",
    "drawStar": "draw_star",
    "drawString": "draw_string",
    "drawThickLine": "draw_line_thick",
}


class WriterNaive:
    """Object to draw shapes on a NaNoPy canvas.

    Public drawing coordinates are Cartesian: ``(0, 0)`` is the bottom-left
    pixel and increasing ``y`` moves upward. SDL uses top-left coordinates, so
    every primitive converts a public ``y`` coordinate to SDL row
    ``canvas_height - 1 - y`` at the rendering boundary. Coordinates are cast
    to integers, but are not clipped to the canvas.

    Closing a canvas invalidates its native SDL pointers. Drawing calls made
    later in the current animation iteration are therefore safe no-ops; they
    never pass a cached, destroyed renderer to SDL_gfx.

    ``writer(canvas)``
    ``canvas``: NaNoPy canvas
    """

    def __init__(self, canvas: CanvasNaive, *, mainloop: Mainloop) -> None:
        self.canvas = canvas
        self._window_name = self.canvas.name
        self._NNP = mainloop

    def __getattr__(self, name: str) -> Callable[..., None]:
        """Resolve deprecated camelCase drawing names without exposing them as fields."""
        replacement = _LEGACY_DRAW_METHODS.get(name)
        if replacement is None:
            raise AttributeError(f"{type(self).__name__!s} has no attribute {name!r}")

        warnings.warn(
            f"{name}() is deprecated and will be removed in a future version. Use {replacement}() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return cast("Callable[..., None]", getattr(self, replacement))

    @property
    def window(self) -> object | None:
        """Return the live SDL window pointer, or ``None`` after closure."""
        if not self.canvas.NNP._canvas_is_active(self.canvas):
            return None
        return self.canvas.window

    @property
    def renderer(self) -> object | None:
        """Return the live SDL renderer pointer, or ``None`` after closure."""
        if not self.canvas.NNP._canvas_is_active(self.canvas):
            return None
        return self.canvas.renderer

    def _active_renderer(self) -> object | None:
        """Return a safe renderer for drawing, or ``None`` after close."""
        return self.renderer

    @property
    def y_size(self) -> int:
        return self.canvas.get_window_size()[1]

    def _to_sdl_y(self, y: float) -> int:
        """Convert a public Cartesian y-coordinate to an SDL pixel row."""
        return int(self.y_size - 1 - y)

    def draw_pixel(self, x: float, y: float, color: Color = Color.white) -> None:
        """Draws pixels of given color on x,y coordinate.
        Casts x, y coordinate to int.
        """
        renderer = self._active_renderer()
        if renderer is None:
            return
        pixelColor(renderer, int(x), self._to_sdl_y(y), color)

    def draw_line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        color: Color = Color.white,
    ) -> None:
        """Draws line of 1 pixel wide between x1,y1 and x2,y2 of given color"""
        renderer = self._active_renderer()
        if renderer is None:
            return
        aalineColor(renderer, int(x1), self._to_sdl_y(y1), int(x2), self._to_sdl_y(y2), color)

    def draw_line_thick(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        width: float,
        color: Color = Color.white,
    ) -> None:
        """Draws line of width pixels wide between x1,y1 and x2,y2 of given color."""
        renderer = self._active_renderer()
        if renderer is None:
            return
        thickLineColor(
            renderer,
            int(x1),
            self._to_sdl_y(y1),
            int(x2),
            self._to_sdl_y(y2),
            int(width),
            color,
        )

    def draw_rectangle(
        self,
        x1: float,
        y1: float,
        width: float,
        height: float,
        color: Color = Color.white,
        filled: bool = False,
        *,
        fill_color: Color | None = None,
    ) -> None:
        """Draw a rectangle whose bottom-left corner is ``(x1, y1)``.

        ``filled=True`` fills with ``color``. Supplying ``fill_color`` requests
        a fill even when ``filled`` is false and preserves ``color`` as a
        separately drawn outline.
        """
        renderer = self._active_renderer()
        if renderer is None:
            return
        if filled or fill_color is not None:
            boxColor(
                renderer,
                int(x1),
                self._to_sdl_y(y1),
                int(x1 + width),
                self._to_sdl_y(y1 + height),
                fill_color if fill_color is not None else color,
            )
            if fill_color is not None:
                rectangleColor(
                    renderer,
                    int(x1),
                    self._to_sdl_y(y1),
                    int(x1 + width),
                    self._to_sdl_y(y1 + height),
                    color,
                )
        else:
            rectangleColor(
                renderer,
                int(x1),
                self._to_sdl_y(y1),
                int(x1 + width),
                self._to_sdl_y(y1 + height),
                color,
            )

    def draw_circle(
        self,
        x: float,
        y: float,
        radius: float,
        color: Color = Color.white,
        filled: bool = False,
        *,
        fill_color: Color | None = None,
    ) -> None:
        """Draw a circle centered at ``(x, y)``.

        ``filled=True`` fills with ``color``. Supplying ``fill_color`` requests
        a fill even when ``filled`` is false and preserves ``color`` as a
        separately drawn outline.
        """
        renderer = self._active_renderer()
        if renderer is None:
            return
        if filled or fill_color is not None:
            filledCircleColor(
                renderer,
                int(x),
                self._to_sdl_y(y),
                int(radius),
                fill_color if fill_color is not None else color,
            )
            if fill_color is not None:
                aacircleColor(renderer, int(x), self._to_sdl_y(y), int(radius), color)
        else:
            aacircleColor(renderer, int(x), self._to_sdl_y(y), int(radius), color)

    def draw_star(
        self,
        x: float,
        y: float,
        radius: float,
        n: int,
        color: Color = Color.white,
        filled: bool = False,
        *,
        fill_color: Color | None = None,
    ) -> None:
        """Draw an n-pointed star centered at ``(x, y)``.

        Supplying ``fill_color`` requests a fill even when ``filled`` is false
        and preserves ``color`` as a separately drawn outline.

        Raises:
            ValueError: If ``n`` is less than three.

        """
        if n < 3:
            raise ValueError("A star requires at least three points")

        rads = (2 * math.pi) / (2 * n)
        points = []
        for i in range(n * 2):
            point_radius = radius / ((i % 2) + 1)
            angle = rads * i
            points.append(
                (
                    x + math.cos(angle) * point_radius,
                    y - math.sin(angle) * point_radius,
                ),
            )

        self.draw_polygon_custom(points, color, filled, fill_color=fill_color)

    def draw_polygon_custom(
        self,
        points: Sequence[tuple[float, float]],
        color: Color = Color.white,
        filled: bool = False,
        *,
        fill_color: Color | None = None,
    ) -> None:
        """Draw a custom polygon from at least three Cartesian points.

        ``points`` uses the same bottom-left coordinate system as every other
        drawing primitive. Integer and floating-point coordinates are accepted
        and converted to SDL's integer coordinates immediately before drawing.
        Supplying ``fill_color`` requests a fill even when ``filled`` is false
        and preserves ``color`` as a separately drawn outline.
        """
        n = len(points)
        if n < 3:
            raise ValueError("A polygon requires at least three points")

        renderer = self._active_renderer()
        if renderer is None:
            return

        xs, ys = zip(*points, strict=True)
        vx = (ctypes.c_int16 * n)(*(int(x) for x in xs))
        vy = (ctypes.c_int16 * n)(*(self._to_sdl_y(y) for y in ys))

        if filled or fill_color is not None:
            filledPolygonColor(
                renderer,
                vx,
                vy,
                n,
                fill_color if fill_color is not None else color,
            )
            if fill_color is not None:
                aapolygonColor(renderer, vx, vy, n, color)
        else:
            aapolygonColor(renderer, vx, vy, n, color)

    def draw_polygon(
        self,
        x: float,
        y: float,
        radius: float,
        n: int,
        color: Color = Color.white,
        filled: bool = False,
        *,
        fill_color: Color | None = None,
    ) -> None:
        """Draw a regular n-sided polygon centered at ``(x, y)``.

        Supplying ``fill_color`` requests a fill even when ``filled`` is false
        and preserves ``color`` as a separately drawn outline.

        Raises:
            ValueError: If ``n`` is less than three.

        """
        if n < 3:
            raise ValueError("A polygon requires at least three points")

        rads = (2 * math.pi) / n
        points = []
        for i in range(n):
            angle = (rads * i) - (math.pi / 2)
            points.append(
                (
                    x + math.cos(angle) * radius,
                    y - math.sin(angle) * radius,
                ),
            )

        self.draw_polygon_custom(points, color, filled, fill_color=fill_color)

    def draw_spline(
        self,
        xs: Iterable[float],
        ys: Iterable[float],
        color: Color = Color.white,
        loop: bool = False,
        filled: bool = False,
        *,
        fill_color: Color | None = None,
    ) -> None:
        """Draw a spline, optionally filling a closed loop.

        ``filled=True`` fills a closed spline with ``color``. Supplying
        ``fill_color`` requests a fill even when ``filled`` is false and
        preserves ``color`` for the spline itself. Filling has no effect when
        ``loop`` is false.
        """
        if self._active_renderer() is None:
            return
        self.spln = Spline(xs, ys, loop)

        active_fill_color = fill_color if fill_color is not None else color
        if loop and (filled or fill_color is not None):
            for x, y in zip(self.spln.insidex, self.spln.insidey, strict=True):
                self.draw_pixel(x, y, active_fill_color)

        for v in zip(self.spln.splinex, self.spln.spliney, strict=True):
            self.draw_pixel(v[0], v[1], color)

    def draw_string(
        self,
        x: float,
        y: float,
        color: Color = Color.white,
        text: str = "placeholder",
    ) -> None:
        """Draws string on location x,y with given color"""
        renderer = self._active_renderer()
        if renderer is None:
            return
        # Ensure the SDL_gfx font is bound to the current renderer when using multiple windows.
        if self.canvas._reload_fonts or self.canvas.NNP.multiple_windows:
            gfxPrimitivesSetFont(None, 0, 0)
            self.canvas._reload_fonts = False
        stringColor(renderer, int(x), self._to_sdl_y(y), str.encode(text), color)
