"""Particles carried along by a flowing spline channel.

Run it with ``nanopy splines`` or::

    from NaNoPy.demos import splines
    splines()
"""

import random as rnd

import numpy as np

from NaNoPy import Canvas, Color, Writer


def demo() -> None:
    """Move particles through a wobbling channel made of two splines.

    Extends the random walk with a flow term: how much the spline moved
    between two frames is added to the particles, so they are dragged along
    with the channel instead of only diffusing.

    Close the window to stop.
    """
    x_size = 800
    y_size = 400

    screen = Canvas("screen1", x_size, y_size, xpos=50, ypos=50)
    pen = Writer(screen)

    x = []
    y = []
    x_part = []
    y_part = []
    radius = 5

    n = 9
    n_part = 100

    for i in range(n):
        x.append(i * (x_size / (n - 1)))
        y.append(y_size / 2)

    for _ in range(n_part):
        x_part.append(rnd.randint(radius, x_size - radius))
        y_part.append(y_size / 2 + rnd.randint(-3, 3))

    print(x)

    first = True
    splinedy = np.array([], dtype=float)

    while screen.running():
        for i in range(len(x)):
            dy = rnd.randint(-3, 3)

            if 0 < i < len(x) - 1:
                y[i] += dy
        if not first:
            splinedy = pen.spln.spliney

        pen.draw_spline(x, np.array(y) - 50, Color.green, False)
        pen.draw_spline(x, np.array(y) + 50, Color.green, False)

        if not first:
            spsize = min(pen.spln.spliney.size, splinedy.size)
            splinedy = pen.spln.spliney[0:spsize] - splinedy[0:spsize]

        if first:
            splinedy = np.zeros(pen.spln.spliney.size)

        first = False

        for i in range(n_part):
            dx = rnd.randint(-5, 5)
            dy = rnd.randint(-5, 5)

            ind = np.nonzero(pen.spln.splinex >= x_part[i])[0][0]

            y_part[i] += splinedy[ind % splinedy.size]

            if (
                y_part[i] + dy < pen.spln.spliney[ind] - (2 * radius)
                and y_part[i] + dy > (pen.spln.spliney[ind] - 100) + (2 * radius)
                and x_part[i] + dx > 0
            ):
                x_part[i] += dx
                y_part[i] += dy

            # flow
            flowdx = 5
            ind2 = np.nonzero(pen.spln.splinex >= (x_part[i] + flowdx) % x_size)[0][0]
            flowdy = pen.spln.spliney[ind2] - pen.spln.spliney[(ind) % pen.spln.splinex.size]

            x_part[i] += flowdx
            y_part[i] += flowdy

            x_part[i] = x_part[i] % x_size

        for i in range(n_part):
            pen.draw_circle(x_part[i], y_part[i], radius, Color.red, True)
            pen.draw_circle(x_part[i], y_part[i], radius - 3, Color.yellow, True)

        screen.update()
        screen.pause(12)
        screen.clear()


if __name__ == "__main__":
    demo()
