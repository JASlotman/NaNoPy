"""Two windows whose balls are pulled towards their own window centre.

Run it with ``nanopy multiple_ball`` or::

    from NaNoPy.demos import multiple_ball
    multiple_ball()
"""

import colorsys
import math
from typing import Any

from NaNoPy import Canvas, Color, Writer


def demo() -> None:
    """Animate one ball per window, each drawn in both windows at once.

    Every ball is attracted to the centre of its own window and damped, so
    dragging a window around whips its ball back. Both windows draw every
    ball, which makes it easy to see that the positions are kept in screen
    coordinates (``Canvas.get_window_pos``).

    Close either window to stop.
    """
    balls: list[dict[str, Any]] = [
        {
            "x_size": 300,
            "y_size": 300,
            "x": 0,
            "y": 0,
            "dy": 0,
            "dx": 0,
        },
        {
            "x_size": 300,
            "y_size": 300,
            "x": 0,
            "y": 0,
            "dy": 0,
            "dx": 0,
        },
    ]

    for i in range(len(balls)):
        ball = balls[i]
        ball["screen"] = Canvas(f"Ball {i}", ball["x_size"], ball["y_size"])
        ball["pen"] = Writer(ball["screen"])

        r, g, b = colorsys.hls_to_rgb((i / 20), 0.5, 1)

        x_i, y_i = ball["screen"].get_window_pos()

        ball["x"] = x_i + ball["x_size"] // 2
        ball["y"] = y_i + ball["y_size"] // 2
        ball["color"] = Color.custom(r=int(r * 255), g=int(g * 255), b=int(b * 255))

    while any(ball["screen"].running() for ball in balls):
        for ball_renderer in balls:
            ball_renderer["screen"].clear()

            x, y = ball_renderer["screen"].get_window_pos()

            center_x = ball_renderer["x_size"] // 2
            center_y = ball_renderer["y_size"] // 2
            dx = center_x - (ball_renderer["x"] - x)
            dy = center_y - (ball_renderer["y"] - y)
            distance = (dx**2 + dy**2) ** 0.5
            theta = math.atan2(dy, dx)

            force = distance * 0.02

            ball_renderer["dx"] *= 0.9
            ball_renderer["dy"] *= 0.9

            ball_renderer["dx"] += math.cos(theta) * force
            ball_renderer["dy"] += math.sin(theta) * force

            ball_renderer["x"] += ball_renderer["dx"]
            ball_renderer["y"] += ball_renderer["dy"]

            for ball in balls:
                ball_renderer["pen"].draw_circle(ball["x"] - x, ball_renderer["y_size"] - (ball["y"] - y), 20, ball["color"], True)

            ball_renderer["screen"].update()


if __name__ == "__main__":
    demo()
