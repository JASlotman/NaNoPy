"""Stress test: how much per-frame Python work a canvas can take.

Run it with ``nanopy efficiency`` or::

    from NaNoPy.demos import efficiency
    efficiency()
"""

import random as rnd

from NaNoPy import Canvas, Color, Writer


def demo() -> None:
    """Sweep a star with a particle trail across the screen, pixel by pixel.

    Every frame redraws 500 background pixels plus a growing particle list,
    which makes the per-frame cost of pure-Python drawing easy to feel.
    Compare it with ``nerve``, which does similar work through numpy.

    Close the window to stop.
    """
    # This is a test file for the NaNoPy library.
    x_size = int(1920 / 2)
    y_size = int(1080 / 2)
    screen = Canvas("Zamkor", x_size, y_size)
    pen = Writer(screen)
    y = y_size / 2
    stars = []
    particles = []  # List to store trailing particles

    stars.extend((rnd.randint(0, x_size), rnd.randint(0, y_size)) for _ in range(500))

    while screen.running():
        for x in range(x_size):
            for i in range(len(stars)):
                pen.draw_pixel(stars[i][0], stars[i][1], Color.white)

            # Add new particles at the star's position
            particles.extend(
                [x, y, rnd.uniform(-1, 0), rnd.uniform(-0.5, 0.5), rnd.randint(5, 300)] for _ in range(5)
            )  # [x, y, x_velocity, y_velocity, lifetime]

            # Update and draw particles
            i = 0
            while i < len(particles):
                particle = particles[i]
                # Update particle position
                particle[0] += particle[2]  # Update x position
                particle[1] += particle[3]  # Update y position
                particle[4] -= 1  # Decrease lifetime

                # Draw the particle
                pen.draw_pixel(int(particle[0]), int(particle[1]), Color.red)

                # Remove particles that have expired
                if particle[4] <= 0:
                    particles.pop(i)
                else:
                    i += 1

            # Draw the star
            pen.draw_star(x, y, 10, 5, Color.yellow, True)
            screen.update()
            screen.clear()
        screen.pause(20)
        screen.clear()
        screen.update()


if __name__ == "__main__":
    demo()
