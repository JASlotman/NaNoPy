"""macOS ARM check: drawing without an animation loop, using the old API.

Run it with ``nanopy mac_arm_ball`` or::

    from NaNoPy.demos import mac_arm_ball
    mac_arm_ball()
"""

# apparently simple not looped operations are braking on macOS arm
# based on one of firs exercises (blue ball)
from NaNoPy import canvas, color, writer


def demo() -> None:
    """Draw a blue ball, clear it after half a second, then wait for the close.

    Written with the deprecated lowercase API (``canvas``/``writer``/``color``
    and ``keepwindow``) on purpose, because that is the form the original
    exercise used. Expect ``DeprecationWarning``s; see ``squares`` for the
    same style of drawing with the current API.

    Close the window to stop.
    """
    width = 800
    height = 800

    screen = canvas("circle", width, height)
    pen = writer(screen)

    pen.draw_circle(width / 2, height / 2, 50, color().blue, True)
    screen.update()  # The screen needs to be updated to see the effect of the clearing

    screen.pause(500)
    screen.clear()
    screen.update()  # The screen needs to be updated to see the effect of the clearing
    screen.keepwindow()


if __name__ == "__main__":
    demo()
