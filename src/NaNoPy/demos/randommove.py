"""Random-walking dots labelled with their own coordinates.

Run it with ``nanopy randommove`` or::

    from NaNoPy.demos import randommove
    randommove()
"""

import random

from NaNoPy import Canvas, Color, Writer


def demo() -> None:
    """Random-walk ten dots and label each with its frame and position.

    Shows a bounded random walk plus ``draw_string`` and ``draw_line``, which
    makes it handy for checking what your simulation is actually doing.

    Close the window to stop.
    """
    x_size = 800
    y_size = 400

    screen = Canvas("Name", x_size, y_size)
    pen = Writer(screen)

    n = 10
    x = []
    y = []

    for _ in range(n):
        x.append(random.randint(0, x_size))
        y.append(random.randint(0, y_size))

    frame = 1

    while screen.running():
        frame += 1
        for i in range(n):
            dx = random.randint(-4, 4)
            dy = random.randint(-4, 4)
            if x[i] + dx > 0 and x[i] + dx < x_size and y[i] + dy > 0 and y[i] + dy < y_size:
                x[i] += dx
                y[i] += dy

        for i in range(n):
            pen.draw_circle(x[i], y[i], 5, Color.green, True)
            pen.draw_string(
                x[i],
                y[i],
                Color.red,
                "f:" + str(frame) + " p: " + str(i) + " x:" + str(x[i]) + " y:" + str(y[i]),
            )
            pen.draw_line(0, y[i], 800, y[i], Color.red)

        screen.update()
        screen.pause(50)
        screen.clear()


if __name__ == "__main__":
    demo()
