"""Static drawing of a custom polygon, a star, and a hexagon.

Run it with ``nanopy funky_polygons`` or::

    from NaNoPy.demos import funky_polygons
    funky_polygons()
"""

from time import sleep

from NaNoPy import Canvas, Color, Writer


def demo() -> None:
    """Draw three polygon shapes, one of them deliberately off-canvas.

    Shows ``draw_polygon_custom`` (arbitrary points), ``draw_star``, and
    ``draw_polygon`` (regular n-gon). The first polygon reaches past the
    window edge on purpose, to show that drawing is clipped.

    The window closes by itself after about three seconds.
    """
    screen = Canvas("funky_polygons.py", 400, 400)
    pen = Writer(screen)

    pen.draw_polygon_custom([(10, 30), (500, 500), (100, 0)], Color.white, True)
    pen.draw_star(100, 100, 20, 5, Color.white, True)
    pen.draw_polygon(20, 20, 20, 6, Color.white, filled=True)

    screen.update()
    sleep(3)

    # Release the window so the next demo starts from a clean mainloop.
    screen.NNP.stop()


if __name__ == "__main__":
    demo()
