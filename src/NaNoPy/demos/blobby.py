import math
import random as rnd

from NaNoPy import Canvas, Color, Writer


def demo() -> None:
    x_size = 800
    y_size = 600

    screen = Canvas("blob", x_size, y_size)
    pen = Writer(screen)

    x = []
    y = []
    radii = []
    angles = []

    x_center = x_size / 2
    y_center = y_size / 2

    point_count = 7
    particle_count = 5

    particle_x = [x_center for _ in range(particle_count)]
    particle_y = [y_center for _ in range(particle_count)]

    for index in range(point_count):
        radius = rnd.randint(100, 120)
        angle = ((2 * math.pi) / point_count) * index
        radii.append(radius)
        angles.append(angle)
        x.append(x_center + math.cos(angle) * radius)
        y.append(y_center + math.sin(angle) * radius)

    try:
        while screen.running():
            for index in range(point_count):
                radius_change = rnd.randint(-5, 5)
                if 50 < radii[index] + radius_change < 250:
                    # Uncomment to animate the outline as well.
                    # radii[index] += radius_change
                    pass
                x[index] = x_center + math.cos(angles[index]) * radii[index]
                y[index] = y_center + math.sin(angles[index]) * radii[index]

            pen.draw_spline(x, y, Color.magenta, loop=True)

            for index in range(particle_count):
                dx = rnd.randint(-5, 5)
                dy = rnd.randint(-5, 5)

                if pen.spln.get_inside(particle_x[index] + dx, particle_y[index] + dy):
                    particle_x[index] += dx
                    particle_y[index] += dy

            for index in range(particle_count):
                pen.draw_circle(
                    particle_x[index],
                    particle_y[index],
                    5,
                    Color.magenta,
                    filled=True,
                )

            screen.update()
            screen.pause(12)
            screen.clear()
    finally:
        screen.NNP.stop()


if __name__ == "__main__":
    demo()
