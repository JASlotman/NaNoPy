import numpy as np
from NaNoPy import Canvas, Writer, Color


def demo() -> None:
    x_size = 800
    y_size = 400

    screen = Canvas("Nerve Pulse", x_size, y_size, xpos=50, ypos=50)
    pen = Writer(screen)
    rng = np.random.default_rng(69696969)

    control_count = 9
    particle_count = 160
    channel_half = 70
    particle_speed = 7.0

    control_x = np.linspace(0, x_size, control_count, dtype=float)
    control_y = np.full(control_count, y_size / 2.0, dtype=float)
    control_bounds = (y_size * 0.25, y_size * 0.75)

    particles_x = rng.uniform(0, x_size, particle_count)
    particles_offset = rng.uniform(-channel_half * 0.25, channel_half * 0.25, particle_count)

    while screen.running():
        jitter = rng.integers(-3, 4, size=control_count)
        control_y[1:-1] = np.clip(
            control_y[1:-1] + jitter[1:-1], control_bounds[0], control_bounds[1]
        )

        wall_color = Color.custom(r=30, g=140, b=200)
        wall_offsets = (-channel_half, -channel_half + 1, channel_half - 1, channel_half)
        for offset in wall_offsets:
            pen.draw_spline(control_x, control_y + offset, wall_color, False)

        pen.draw_spline(control_x, control_y, Color.white, False)
        curve_x = np.asarray(pen.spln.splinex, dtype=float)
        curve_y = np.asarray(pen.spln.spliney, dtype=float)

        drift_x = rng.normal(0.0, 0.4, particle_count)
        particles_x = (particles_x + particle_speed + drift_x) % x_size

        idx = np.searchsorted(curve_x, particles_x, side="left")
        idx = np.clip(idx, 1, curve_x.size - 2)

        segment_x0 = curve_x[idx - 1]
        segment_x1 = curve_x[idx + 1]
        mix = np.clip((particles_x - segment_x0) / (segment_x1 - segment_x0), 0.0, 1.0)
        segment_y0 = curve_y[idx - 1]
        segment_y1 = curve_y[idx + 1]
        particles_y = (1.0 - mix) * segment_y0 + mix * segment_y1
        particles_y += particles_offset

        glow_color = Color.custom(r=255, g=180, b=20, a=100)
        spark_color = Color.custom(r=255, g=255, b=200, a=220)
        for px, py in zip(particles_x, particles_y):
            pen.draw_circle(px, py, 6, glow_color, True)
            pen.draw_star(px, py, 4, 5, spark_color, True)

        anchor_color = Color.custom(r=90, g=220, b=255, a=180)
        for cx, cy in zip(control_x[1:-1], control_y[1:-1]):
            pen.draw_circle(cx, cy, 3, anchor_color, True)

        screen.update()
        screen.pause(12)
        screen.clear()


if __name__ == "__main__":
    demo()
