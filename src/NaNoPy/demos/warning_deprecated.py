"""Shows the deprecation warnings raised by the old lowercase API.

Run it with ``python -m NaNoPy.demos.warning_deprecated`` or::

    from NaNoPy.demos import warning_deprecated
    warning_deprecated()
"""

import warnings
from time import sleep

from NaNoPy import canvas, writer


def demo() -> None:
    """Draw one circle with the deprecated ``canvas``/``writer`` classes.

    Both constructors raise a ``DeprecationWarning``: use ``Canvas`` and
    ``Writer`` instead. The warnings are unsilenced here on purpose, because
    Python hides ``DeprecationWarning`` unless it comes from the main script.

    The window closes by itself after three seconds.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("always", DeprecationWarning)
        screen = canvas("title", 200, 200)
        pen = writer(screen)

    pen.draw_circle(50, 50, 10)

    screen.update()

    sleep(3)

    # Release the window so the next demo starts from a clean mainloop.
    screen.NNP.stop()


if __name__ == "__main__":
    demo()
