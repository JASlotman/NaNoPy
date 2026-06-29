from NaNoPy import Canvas, Writer, Color


def demo() -> None:
    x_size = 800
    y_size = 400

    screen = Canvas("screen1", x_size, y_size, xpos=50, ypos=50)
    pen = Writer(screen)

    # help(canvas)
    # help(pen)
    # help(color)

    green = Color.green
    green_mid = Color.custom(r=0, g=255, a=150)
    green_mid_light = Color.custom(r=0, g=255, a=100)
    green_light = Color.custom(r=0, g=255, a=50)
    green_blue = Color.custom(g=255, b=155)

    pen.draw_rectangle(50, 50, 50, 50, green, False)
    pen.draw_rectangle(100, 50, 50, 50, green_mid, True)
    pen.draw_rectangle(151, 50, 50, 50, green_mid_light, True)
    pen.draw_rectangle(202, 50, 50, 50, green_light, True)
    pen.draw_polygon(50, 150, 25, 4, green, False)
    pen.draw_polygon(100, 150, 25, 4, green_mid, True)
    pen.draw_polygon(151, 150, 25, 4, green_mid_light, True)
    pen.draw_polygon(202, 150, 25, 4, green_light, True)
    pen.draw_polygon(50, 250, 25, 6, green, False)
    pen.draw_polygon(100, 250, 25, 6, green_mid, True)
    pen.draw_polygon(151, 250, 25, 6, green_mid_light, True)
    pen.draw_polygon(202, 250, 25, 6, green_light, True)

    # closed and open splines
    pen.draw_spline([400, 500, 500, 400], [200, 200, 300, 300], Color.red, True, True)
    pen.draw_spline([600, 700, 700, 600], [200, 200, 300, 300], green_blue, True, False)
    pen.draw_spline([400, 500, 600, 700], [100, 50, 100, 50], Color.yellow, False, False)

    # red points at spline anchors
    pen.draw_circle(400, 200, 5, Color.red, True)
    pen.draw_circle(500, 200, 5, Color.red, True)
    pen.draw_circle(500, 300, 5, Color.red, True)
    pen.draw_circle(400, 300, 5, Color.red, True)

    # green points at spline control points
    pen.draw_circle(600, 200, 5, green_blue, True)
    pen.draw_circle(700, 200, 5, green_blue, True)
    pen.draw_circle(700, 300, 5, green_blue, True)
    pen.draw_circle(600, 300, 5, green_blue, True)

    screen.update()
    screen.keep_window()


if __name__ == "__main__":
    demo()
