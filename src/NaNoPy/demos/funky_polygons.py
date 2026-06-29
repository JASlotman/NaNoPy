from NaNoPy import Canvas, Writer, Color
from time import sleep

def demo() -> None:
    screen = Canvas("funky_polygons.py", 400, 400)
    pen = Writer(screen)

    pen.draw_polygon_custom([(10, 30), (500, 500), (100, 0)], Color.white, True)
    pen.draw_star(100, 100, 20, 5, Color.white, True)
    pen.draw_polygon(20, 20, 20, 6, Color.white, filled=True)

    screen.update()
    sleep(3)

if __name__ == "__main__":
    demo()