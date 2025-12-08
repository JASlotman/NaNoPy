from NaNoPy import Canvas, Writer, Color
import random as rnd


def demo() -> None:
    # This is a test file for the NaNoPy library.
    x_size = int(1920 / 2)
    y_size = int(1080 / 2)
    screen = Canvas("Zamkor", x_size, y_size)
    pen = Writer(screen)
    y = y_size / 2
    stars = []
    particles = []  # List to store trailing particles

    for i in range(500):
        stars.append((rnd.randint(0, x_size), rnd.randint(0, y_size)))

    while screen.running():
        for x in range(x_size):
            for i in range(len(stars)):
                pen.draw_pixel(stars[i][0], stars[i][1], Color.white)

            # Add new particles at the star's position
            for _ in range(5):  # Add 5 particles each frame
                particles.append(
                    [x, y, rnd.uniform(-1, 0), rnd.uniform(-0.5, 0.5), rnd.randint(5, 300)]
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
