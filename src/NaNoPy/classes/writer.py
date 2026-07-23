from sdl2.sdlgfx import pixelColor
from sdl2.sdlgfx import aalineColor
from sdl2.sdlgfx import thickLineColor
from sdl2.sdlgfx import boxColor
from sdl2.sdlgfx import rectangleColor
from sdl2.sdlgfx import filledPolygonColor
from sdl2.sdlgfx import filledCircleColor
from sdl2.sdlgfx import aapolygonColor
from sdl2.sdlgfx import aacircleColor
from sdl2.sdlgfx import stringColor
from sdl2.sdlgfx import gfxPrimitivesSetFont

import ctypes
import math
import warnings

from NaNoPy.classes.canvas import CanvasNaive
from NaNoPy.classes.mainloop import Mainloop
from NaNoPy.classes.spline import Spline
from NaNoPy.classes.color import Color

from typing import Iterable, Sequence


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

    def __init__(self, canvas: CanvasNaive, *, NNP: Mainloop):
        self.canvas = canvas
        self._window_name = self.canvas.name
        self._NNP = NNP

    @property
    def window(self):
        """Return the live SDL window pointer, or ``None`` after closure."""

        if not self.canvas.NNP._canvas_is_active(self.canvas):
            return None
        return self.canvas.window

    @property
    def renderer(self):
        """Return the live SDL renderer pointer, or ``None`` after closure."""

        if not self.canvas.NNP._canvas_is_active(self.canvas):
            return None
        return self.canvas.renderer

    def _active_renderer(self):
        """Return a safe renderer for drawing, or ``None`` after close."""

        return self.renderer

    @property
    def y_size(self):
        return self.canvas.get_window_size()[1]

    def _to_sdl_y(self, y) -> int:
        """Convert a public Cartesian y-coordinate to an SDL pixel row."""
        return int(self.y_size - 1 - y)

    def draw_pixel(self, x, y, color=Color.white) -> None:
        """Draws pixels of given color on x,y coordinate.
        Casts x, y coordinate to int.
        """
        renderer = self._active_renderer()
        if renderer is None:
            return
        pixelColor(renderer, int(x), self._to_sdl_y(y), color)

    def drawPixel(self, x, y, color=Color.white) -> None:
        """(deprecated, use draw_pixel() instead)

        Draws pixels of given color on x,y coordinate"""

        warnings.warn(
            "drawPixel() is deprecated and will be removed in a future version. "
            "Use draw_pixel() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.draw_pixel(x, y, color)

    def draw_line(self, x1, y1, x2, y2, color=Color.white) -> None:
        """Draws line of 1 pixel wide between x1,y1 and x2,y2 of given color"""
        renderer = self._active_renderer()
        if renderer is None:
            return
        aalineColor(
            renderer, int(x1), self._to_sdl_y(y1), int(x2), self._to_sdl_y(y2), color
        )

    def drawLine(self, x1, y1, x2, y2, color=Color.white) -> None:
        """(deprecated, use draw_line() instead)

        Draws line of 1 pixel wide between x1,y1 and x2,y2 of given color.
        """

        warnings.warn(
            "drawLine() is deprecated and will be removed in a future version. "
            "Use draw_line() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.draw_line(x1, y1, x2, y2, color)

    def draw_line_thick(self, x1, y1, x2, y2, width, color=Color.white) -> None:
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

    def drawThickLine(self, x1, y1, x2, y2, w, color=Color.white) -> None:
        """(deprecated, use draw_line_thick() instead)

        Draws line of w pixels wide between x1,y1 and x2,y2 of given color.
        """

        warnings.warn(
            "drawThickLine() is deprecated and will be removed in a future version. "
            "Use draw_line_thick() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.draw_line_thick(x1, y1, x2, y2, w, color)

    def draw_rectangle(self, x1, y1, width, height, color=Color.white, filled: bool=False) -> None:
        """Draws rectangle with x1,y1 being the bottom left corner w being the width and h the height and set filled to true to fill it with given color"""
        renderer = self._active_renderer()
        if renderer is None:
            return
        if filled:
            boxColor(
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

    def drawRectangle(self, x1, y1, w, h, color=Color.white, filled: bool=False) -> None:
        """(deprecated, use draw_rectangle() instead)
        Draws rectangle with x1,y1 being the bottom-left corner, w being the
        width and h the height, and set filled to true to fill it with the
        given color.
        """

        warnings.warn(
            "drawRectangle() is deprecated and will be removed in a future version. "
            "Use draw_rectangle() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.draw_rectangle(x1, y1, w, h, color, filled)

    def draw_circle(self, x, y, radius, color=Color.white, filled: bool=False) -> None:
        """Draws circle with a given radius, and x,y being the centre location and set filled to true to fill it with given color"""
        renderer = self._active_renderer()
        if renderer is None:
            return
        if filled:
            filledCircleColor(renderer, int(x), self._to_sdl_y(y), int(radius), color)
        else:
            aacircleColor(renderer, int(x), self._to_sdl_y(y), int(radius), color)

    def drawCircle(self, x, y, r, color=Color.white, filled: bool=False) -> None:
        """(deprecated, use draw_circle() instead)
        Draws circle with radius r, and x,y being the centre location and set filled to true to fill it with given color"""

        warnings.warn(
            "drawCircle() is deprecated and will be removed in a future version. "
            "Use draw_circle() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.draw_circle(x, y, r, color, filled)

    def draw_star(self, x, y, radius, n, color=Color.white, filled: bool=False) -> None:
        """Draw an n-pointed star centered at ``(x, y)``.

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
                )
            )

        self.draw_polygon_custom(points, color, filled)

    def drawStar(self, x, y, r, n, color=Color.white, filled: bool=False) -> None:
        """(deprecated, use draw_star() instead)

        Draws star with n points with radius r, and x,y being the centre location and set filled to true to fill it with given color
        """

        warnings.warn(
            "drawStar() is deprecated and will be removed in a future version. "
            "Use draw_star() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.draw_star(x, y, r, n, color, filled)

    def draw_polygon_custom(
        self,
        points: Sequence[tuple[float, float]],
        color=Color.white,
        filled: bool = False,
    ) -> None:
        """Draw a custom polygon from at least three Cartesian points.

        ``points`` uses the same bottom-left coordinate system as every other
        drawing primitive. Integer and floating-point coordinates are accepted
        and converted to SDL's integer coordinates immediately before drawing.
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

        if filled:
            filledPolygonColor(renderer, vx, vy, n, color)
        else:
            aapolygonColor(renderer, vx, vy, n, color)

    def draw_polygon(self, x, y, radius, n, color=Color.white, filled: bool=False) -> None:
        """Draw a regular n-sided polygon centered at ``(x, y)``.

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
                )
            )

        self.draw_polygon_custom(points, color, filled)

    def drawPolygon(self, x, y, r, n, color=Color.white, filled: bool=False) -> None:
        """(deprecated, use draw_polygon instead)
        Draws n sided polygon with radius r, and x,y being the centre location and set filled to true to fill it with given color"""

        warnings.warn(
            "drawPolygon() is deprecated and will be removed in a future version. "
            "Use draw_polygon() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.draw_polygon(x, y, r, n, color, filled)

    def draw_spline(
        self,
        xs: Iterable,
        ys: Iterable,
        color=Color.white,
        loop: bool = False,
        filled: bool = False,
        *,
        fill_color=None,
    ) -> None:
        """Draw a spline, optionally filling a closed loop with a separate color."""
        if self._active_renderer() is None:
            return
        self.spln = Spline(xs, ys, loop)

        active_fill_color = fill_color if fill_color is not None else color
        if loop and (filled or fill_color is not None):
            for x, y in zip(self.spln.insidex, self.spln.insidey, strict=True):
                self.draw_pixel(x, y, active_fill_color)

        for v in zip(self.spln.splinex, self.spln.spliney, strict=True):
            self.draw_pixel(v[0], v[1], color)

    def drawSpline(self, xs: Iterable, ys: Iterable, color=Color.white, loop: bool=False, filled: bool=False) -> None:
        """(deprecated, use draw_spline() instead)

        Draws spline through list of coordinates xs,ys of given color, loop false gives a line, loop true gives a closed loop
        coordinate information of complete line available in writer.spln object"""

        warnings.warn(
            "drawSpline() is deprecated and will be removed in a future version. "
            "Use draw_spline() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.draw_spline(xs, ys, color, loop, filled)

    def draw_string(self, x, y, color=Color.white, text: str="placeholder") -> None:
        """Draws string on location x,y with given color"""
        renderer = self._active_renderer()
        if renderer is None:
            return
        # Ensure the SDL_gfx font is bound to the current renderer when using multiple windows.
        if self.canvas._reload_fonts or self.canvas.NNP.multiple_windows:
            gfxPrimitivesSetFont(None, 0, 0)
            self.canvas._reload_fonts = False
        stringColor(renderer, int(x), self._to_sdl_y(y), str.encode(text), color)

    def drawString(self, x, y, color=Color.white, text: str="placeholder") -> None:
        """(deprecated, use draw_string() instead)

        Draws string on location x,y with given color"""
        warnings.warn(
            "drawString() is deprecated and will be removed in a future version. "
            "Use draw_string() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.draw_string(x, y, color, text)
