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

import ctypes
import math
import warnings

from NaNoPy.classes.canvas import CanvasNaive
from NaNoPy.classes.mainloop import Mainloop
from NaNoPy.classes.spline import Spline

from typing import Iterable


class WriterNaive:
    """Object to draw shapes on a nanopy canvas

    writer(canvas)
    canvas: nanopy canvas
    """

    def __init__(self, canvas: CanvasNaive, *, NNP: Mainloop):
        self.canvas = canvas
        self.window = canvas.window
        self.renderer = canvas.renderer

        self._window_name = self.canvas.name
        self._NNP = NNP

    @property
    def y_size(self):
        return self.canvas.get_window_size()[1]

    def draw_pixel(self, x, y, color) -> None:
        """Draws pixels of given color on x,y coordinate.
        Casts x, y coordinate to int.
        """
        pixelColor(self.renderer, int(x), int(self.y_size - y), color)

    def drawPixel(self, x, y, color) -> None:
        """(deprecated, use draw_pixel() instead)

        Draws pixels of given color on x,y coordinate"""

        warnings.warn(
            "drawPixel() is deprecated and will be removed in a future version. "
            "Use draw_pixel() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.draw_pixel(x, y, color)

    def draw_line(self, x1, y1, x2, y2, color) -> None:
        """Draws line of 1 pixel wide between x1,y1 and x2,y2 of given color"""
        aalineColor(
            self.renderer, int(x1), int(self.y_size - y1), int(x2), int(self.y_size - y2), color
        )

    def drawLine(self, x1, y1, x2, y2, color) -> None:
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

    def draw_line_thick(self, x1, y1, x2, y2, width, color) -> None:
        """Draws line of width pixels wide between x1,y1 and x2,y2 of given color."""
        thickLineColor(
            self.renderer,
            int(x1),
            int(self.y_size - y1),
            int(x2),
            int(self.y_size - y2),
            int(width),
            color,
        )

    def drawThickLine(self, x1, y1, x2, y2, w, color) -> None:
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

    def draw_rectangle(self, x1, y1, width, height, color, filled: bool) -> None:
        """Draws rectangle with x1,y1 being the bottom left corner w being the width and h the height and set filled to true to fill it with given color"""
        if filled:
            boxColor(
                self.renderer,
                int(x1),
                int(self.y_size - y1),
                int(x1 + width),
                int((self.y_size - (y1 + height))),
                color,
            )
        else:
            rectangleColor(
                self.renderer,
                int(x1),
                int(self.y_size - y1),
                int(x1 + width),
                int((self.y_size - (y1 + height))),
                color,
            )

    def drawRectangle(self, x1, y1, w, h, color, filled: bool) -> None:
        """(deprecated, use draw_rectangle() instead)
        Draws rectangle with x1,y1 being the top left corner w being the width and h the height and set filled to true to fill it with given color"""

        warnings.warn(
            "drawRectangle() is deprecated and will be removed in a future version. "
            "Use draw_rectangle() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.draw_rectangle(x1, y1, w, h, color, filled)

    def draw_circle(self, x, y, radius, color, filled: bool) -> None:
        """Draws circle with a given radius, and x,y being the centre location and set filled to true to fill it with given color"""
        if filled:
            filledCircleColor(self.renderer, int(x), int(self.y_size - y), int(radius), color)
        else:
            aacircleColor(self.renderer, int(x), int(self.y_size - y), int(radius), color)

    def drawCircle(self, x, y, r, color, filled: bool) -> None:
        """(deprecated, use draw_circle() instead)
        Draws circle with radius r, and x,y being the centre location and set filled to true to fill it with given color"""

        warnings.warn(
            "drawCircle() is deprecated and will be removed in a future version. "
            "Use draw_circle() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.draw_circle(x, y, r, color, filled)

    def draw_star(self, x, y, radius, n, color, filled: bool) -> None:
        """Draws a n-pointed star with with a given radius, and x,y being the centre location and set filled to true to fill it with given color"""
        rads = (2 * math.pi) / (2 * n)
        xs = []
        ys = []

        for i in range(n * 2):
            rad = radius / ((i % 2) + 1)
            xs.append(int(x + math.cos(rads * i) * rad))
            ys.append(int((self.y_size) - y + math.sin(rads * i) * rad))

        vx = (ctypes.c_int16 * len(xs))(*xs)
        vy = (ctypes.c_int16 * len(ys))(*ys)

        if filled:
            filledPolygonColor(self.renderer, vx, vy, n * 2, color)
        else:
            aapolygonColor(self.renderer, vx, vy, n * 2, color)

    def drawStar(self, x, y, r, n, color, filled: bool) -> None:
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

    def draw_polygon_regular(self, x, y, radius, n, color, filled: bool) -> None:
        """Draws n sided polygon with radius r, and x,y being the centre location and set filled to true to fill it with given color"""
        rads = (2 * math.pi) / n
        xs = []
        ys = []

        for i in range(n):
            xs.append(int(x + math.cos((rads * i) - (math.pi / 2)) * radius))
            ys.append(int((self.y_size) - y + math.sin((rads * i) - (math.pi / 2)) * radius))

        vx = (ctypes.c_int16 * len(xs))(*xs)
        vy = (ctypes.c_int16 * len(ys))(*ys)

        if filled:
            filledPolygonColor(self.renderer, vx, vy, n, color)
        else:
            aapolygonColor(self.renderer, vx, vy, n, color)

    def drawPolygonRegular(self, x, y, r, n, color, filled: bool) -> None:
        """(deprecated, use draw_polygon instead)
        Draws n sided polygon with radius r, and x,y being the centre location and set filled to true to fill it with given color"""

        warnings.warn(
            "drawPolygon() is deprecated and will be removed in a future version. "
            "Use draw_polygon() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.draw_polygon_regular(x, y, r, n, color, filled)

    def draw_spline(self, xs: Iterable, ys: Iterable, color, loop: bool, filled: bool) -> None:
        """Draws spline through list of coordinates xs,ys of given color, loop false gives a line, loop true gives a closed loop
        coordinate information of complete line available in writer.spln object"""
        self.spln = Spline(xs, ys, loop)
        for v in zip(self.spln.splinex, self.spln.spliney):
            self.draw_pixel(v[0], v[1], color)
        if loop and filled:
            for v in zip(self.spln.insidex, self.spln.insidey):
                self.draw_pixel(v[0], v[1], color)

    def drawSpline(self, xs: Iterable, ys: Iterable, color, loop: bool, filled: bool) -> None:
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

    def draw_string(self, x, y, color, text: str) -> None:
        """Draws string on location x,y with given color"""

        self.canvas._reload_fonts = True

        stringColor(self.renderer, int(x), int(self.y_size - y), str.encode(text), color)

    def drawString(self, x, y, color, text: str) -> None:
        """(deprecated, use draw_string() instead)

        Draws string on location x,y with given color"""
        warnings.warn(
            "drawString() is deprecated and will be removed in a future version. "
            "Use draw_string() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.draw_string(x, y, color, text)
