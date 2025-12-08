from NaNoPy import Canvas, Writer, Color
import random


def demo() -> None:
    xSize = 800
    ySize = 400

    screen = Canvas("Name", xSize, ySize)
    pen = Writer(screen)

    n = 10
    x = []
    y = []

    for i in range(n):
        x.append(random.randint(0, xSize))
        y.append(random.randint(0, ySize))

    frame = 1

    while screen.running():
        frame += 1
        for i in range(n):
            dx = random.randint(-4, 4)
            dy = random.randint(-4, 4)
            if x[i] + dx > 0 and x[i] + dx < xSize and y[i] + dy > 0 and y[i] + dy < ySize:
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
