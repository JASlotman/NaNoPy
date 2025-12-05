from NaNoPy import Canvas, Writer, Color


def demo() -> None:
    x_size = 800
    y_size = 400

    screen = Canvas("screen1", x_size, y_size, xpos = 50, ypos = 50)
    pen = Writer(screen)

    #help(canvas)
    #help(pen)
    #help(color)


    green = Color.green
    green_mid = Color.custom(r=0,g=255,a=150)
    green_mid_light = Color.custom(r=0,g=255,a=100)
    green_light = Color.custom(r=0,g=255,a=50)

    pen.draw_rectangle(50, 50, 50, 50, green, False)
    pen.draw_rectangle(100, 50,50,50, green_mid, True)
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

    pen.draw_spline(
        [400, 500, 500, 400], 
        [200, 200,300, 300],
        Color.red,
        True,
        True
        )

    pen.draw_circle(400, 200, 5, Color.red, True)
    pen.draw_circle(400, 300, 5, Color.red, True)
    pen.draw_circle(500, 300, 5, Color.red, True)
    pen.draw_circle(500, 200, 5, Color.red, True)

    screen.update()
    screen.keep_window()

if __name__ == '__main__':
    demo()