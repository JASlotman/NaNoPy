"""Reproduces a macOS-only problem with static drawings.

Run it with ``nanopy mac_arm_problem`` or::

    from NaNoPy.demos import mac_arm_problem
    mac_arm_problem()
"""

from NaNoPy import Canvas, Color, Writer


def demo() -> None:
    """Draw a line and a dot once, then keep the window open.

    On macOS the drawing can stay invisible until the window receives another
    event, which is what this demo is meant to expose. Everywhere else it is
    simply a static picture.

    Close the window to stop.
    """
    x_size = 800
    y_size = 500

    screen = Canvas("this shows the mac problem", x_size, y_size)
    pen = Writer(screen)

    pen.draw_line(10, 150, 710, 490, Color.red)
    pen.draw_circle(600, 290, 5, Color.green, True)
    screen.update()
    screen.keep_window()


if __name__ == "__main__":
    demo()
