import math
import warnings
from typing import Iterable, SupportsFloat, SupportsInt, Union

import numpy as np
from numpy.typing import NDArray

NumberLike = Union[int, float, SupportsFloat, SupportsInt]
Array1D = NDArray[np.float64]


class Spline:
    """Spline class for generating a spline through given points."""

    def __init__(self, xs: Iterable[NumberLike], ys: Iterable[NumberLike], loop: bool) -> None:
        self.x: Array1D = np.asarray(list(xs), dtype=float)
        self.y: Array1D = np.asarray(list(ys), dtype=float)
        self.loop = loop

        if self.x.ndim != 1 or self.y.ndim != 1:
            raise ValueError("Spline expects 1D coordinate sequences.")
        if self.x.size != self.y.size:
            raise ValueError("xs and ys must have the same length.")
        if self.x.size < 2:
            raise ValueError("At least two anchors are required to build a spline.")

        self._segment_count = self.x.size if loop else self.x.size - 1
        if self._segment_count <= 0:
            raise ValueError("Open splines require at least two anchors.")

        kx, ky = self._solve_tangents()
        self.ax = self.x.copy()
        self.ay = self.y.copy()
        self.bx = kx
        self.by = ky

        kx_next = np.roll(kx, -1)
        ky_next = np.roll(ky, -1)
        x_next = np.roll(self.x, -1)
        y_next = np.roll(self.y, -1)

        self.cx = 3 * (x_next - self.x) - 2 * kx - kx_next
        self.cy = 3 * (y_next - self.y) - 2 * ky - ky_next
        self.dx = 2 * (self.x - x_next) + kx + kx_next
        self.dy = 2 * (self.y - y_next) + ky + ky_next

        self._sample_segments()

        if loop:
            self.getInsidePix()

    def _solve_tangents(self) -> tuple[Array1D, Array1D]:
        n = self.x.size
        matrix = np.diag(np.full(n, 4.0))
        ones = np.ones(n - 1)
        matrix += np.diag(ones, 1) + np.diag(ones, -1)

        rhs_x = 3.0 * (np.roll(self.x, -1) - np.roll(self.x, 1))
        rhs_y = 3.0 * (np.roll(self.y, -1) - np.roll(self.y, 1))

        if self.loop:
            matrix[0, -1] = 1.0
            matrix[-1, 0] = 1.0
        else:
            matrix[0, 0] = 2.0
            matrix[-1, -1] = 2.0
            rhs_x[0] = 3.0 * (self.x[1] - self.x[0])
            rhs_x[-1] = 3.0 * (self.x[-1] - self.x[-2])
            rhs_y[0] = 3.0 * (self.y[1] - self.y[0])
            rhs_y[-1] = 3.0 * (self.y[-1] - self.y[-2])

        kx = np.linalg.solve(matrix, rhs_x)
        ky = np.linalg.solve(matrix, rhs_y)
        return kx, ky

    def _sample_segments(self) -> None:
        indices = np.arange(self._segment_count)
        x_next = np.roll(self.x, -1)
        y_next = np.roll(self.y, -1)
        deltas = np.maximum(np.abs(x_next - self.x), np.abs(y_next - self.y))
        counts = np.maximum(2, np.ceil(deltas[indices] * 2.5).astype(int))

        splinex = []
        spliney = []
        splinedydx = []

        for idx, sample_count in zip(indices, counts):
            t = np.linspace(0.0, 1.0, num=sample_count, endpoint=True)
            x_values = self._eval_cubic(self.ax[idx], self.bx[idx], self.cx[idx], self.dx[idx], t)
            y_values = self._eval_cubic(self.ay[idx], self.by[idx], self.cy[idx], self.dy[idx], t)
            dx_dt = self._eval_derivative(self.bx[idx], self.cx[idx], self.dx[idx], t)
            dy_dt = self._eval_derivative(self.by[idx], self.cy[idx], self.dy[idx], t)
            splinex.append(x_values)
            spliney.append(y_values)
            splinedydx.append(dy_dt / dx_dt)

        self.splinex = np.concatenate(splinex)
        self.spliney = np.concatenate(spliney)
        self.splinedydx = np.concatenate(splinedydx)

    @staticmethod
    def _eval_cubic(a: float, b: float, c: float, d: float, t: Array1D) -> Array1D:
        return ((d * t + c) * t + b) * t + a

    @staticmethod
    def _eval_derivative(b: float, c: float, d: float, t: Array1D) -> Array1D:
        return ((3.0 * d * t) + 2.0 * c) * t + b

    def get_inside_pixels(self) -> None:
        if not self.loop or self.splinex.size == 0:
            self.insidex = np.array([], dtype=float)
            self.insidey = np.array([], dtype=float)
            return

        order = np.argsort(self.spliney)
        sorted_y = self.spliney[order]
        sorted_x = self.splinex[order]

        min_x = float(np.min(self.splinex))
        max_x = float(np.max(self.splinex))
        min_y = float(np.min(self.spliney))
        max_y = float(np.max(self.spliney))

        height = max(1, int(math.ceil(max_y - min_y)) + 1)
        width = max(1, int(math.ceil(max_x - min_x)) + 1)

        mins = np.full(height, float(width))
        maxs = np.zeros(height)

        local_x = sorted_x - min_x
        local_y = sorted_y - min_y
        rows = np.clip(np.ceil(local_y).astype(int), 0, height - 1)

        np.minimum.at(mins, rows, local_x)
        np.maximum.at(maxs, rows, local_x)

        fill_x = []
        fill_y = []
        for row in range(height):
            left = math.floor(mins[row])
            right = math.ceil(maxs[row])
            if right <= left:
                continue
            xs = np.arange(left, right, dtype=float) + min_x
            ys = np.full(xs.size, row + min_y, dtype=float)
            fill_x.append(xs)
            fill_y.append(ys)

        if fill_x:
            self.insidex = np.concatenate(fill_x)
            self.insidey = np.concatenate(fill_y)
        else:
            self.insidex = np.array([], dtype=float)
            self.insidey = np.array([], dtype=float)

    def get_inside(self, x: float, y: float) -> bool:
        if not self.loop or self.splinex.size == 0:
            return False

        x_coords = self.splinex
        y_coords = self.spliney
        x_next = np.roll(x_coords, -1)
        y_next = np.roll(y_coords, -1)

        intersects = (y_coords > y) != (y_next > y)
        if not np.any(intersects):
            return False

        denom = y_next - y_coords
        with np.errstate(divide="ignore", invalid="ignore"):
            xints = x_coords + (y - y_coords) * (x_next - x_coords) / denom
        xints = np.where(intersects, xints, np.nan)
        crossings = np.count_nonzero((x < xints))
        return bool(crossings % 2)

    def getInside(self, x: float, y: float) -> bool:
        warnings.warn(
            "getInside is deprecated and will be removed in a future release; use get_inside instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_inside(x, y)

    def getInsidePix(self) -> None:
        warnings.warn(
            "getInsidePix is deprecated and will be removed in a future release; use get_inside_pixels instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_inside_pixels()
