#simple test
from NaNoPy import Canvas, Writer, Color


def demo() -> None:
    xSize = 800
    ySize = 400

    screen_main = Canvas("screen1", xSize, ySize, xpos=50, ypos=50)
    screen_side = Canvas("screen2", xSize, ySize, xpos=50 + xSize, ypos=50)
    pen_main = Writer(screen_main)
    pen_side = Writer(screen_side)

    while screen_main.running():
        pen_main.draw_circle(100, 100, 60, Color.green, True)
        pen_main.draw_string(100, 100, Color.red, "Hello")
        pen_main.draw_line(0, 200, 800, 200, Color.green)
        screen_main.update()
        screen_main.pause(500)
        screen_main.clear()
        screen_main.update()
        screen_main.pause(500)
        pen_side.draw_circle(100, 100, 60, Color.green, True)
        pen_side.draw_string(100, 100, Color.white, "World")
        screen_side.update()
        screen_side.pause(500)
        screen_side.clear()
        screen_side.update()
        screen_side.pause(500)

if __name__ == '__main__':
    demo()