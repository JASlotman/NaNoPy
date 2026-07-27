"""Six ways to find colliding particles, from a double loop to grid helpers.

Every variant simulates binding particles and draws the same picture, so you
can compare both the code and the runtime. ``collision_benchmark`` runs them
all in sequence and prints how long each one took.

Run the benchmark with ``python -m NaNoPy.demos.collision_demo`` or import the
variant you want::

    from NaNoPy.demos import collision_benchmark, collision_iterator_single

    collision_iterator_single(n_steps=200, n=1000)
    collision_benchmark()
"""

import math
import random as rnd
from collections.abc import Iterable
from dataclasses import dataclass, field
from math import ceil, sqrt
from random import randint, random
from time import perf_counter

from NaNoPy import NNP, Canvas, Color, Writer, apply_to_close_pairs, get_close_pairs


@dataclass
class Particle:
    x: int
    y: int
    bound: bool = False
    stepsize: int = 4
    p_unbind = 0.05
    radius = 3
    color_bound: Color = Color.red
    color_unbound: Color = Color.green
    particle_type: int = 0
    binding_partners: list[int] = field(default_factory=list)

    @classmethod
    def from_random(
        cls,
        xsize: int,
        ysize: int,
        color_bound: Color = color_bound,
        color_unbound: Color = color_unbound,
        particle_type: int = particle_type,
        binding_partners: Iterable[int] = (),
    ) -> "Particle":
        return cls(
            x=randint(0, xsize),
            y=randint(0, ysize),
            color_bound=color_bound,
            color_unbound=color_unbound,
            particle_type=particle_type,
            binding_partners=list(binding_partners),
        )

    @property
    def pos(self) -> tuple[int, int]:
        return self.x, self.y

    def rw_step_in_box(self, xsize: int, ysize: int) -> None:
        """Slightly changed from original logic. Now particles can rejects part of
        step that would take them out of box instead of whole step.
        Also, 0 is now an allowed ordinate.
        """
        # don't move if bound
        if self.bound:
            return

        # propose positions
        x_proposed = self.x + randint(-self.stepsize, self.stepsize)
        y_proposed = self.y + randint(-self.stepsize, self.stepsize)

        # set new position conditionally
        self.x = x_proposed if 0 <= x_proposed < xsize else self.x
        self.y = y_proposed if 0 <= y_proposed < ysize else self.y

    def attempt_unbinding(self) -> None:
        self.bound = False if random() < self.p_unbind else self.bound

    @property
    def color(self) -> Color:
        return self.color_bound if self.bound else self.color_unbound


def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def attempt_binding(p1: Particle, p2: Particle, maxdist: float) -> None:

    # check for bound
    if p1.bound or p2.bound:
        return

    # measure distance to determine whether to bind
    if distance(*p1.pos, *p2.pos) < maxdist:
        p1.bound = True
        p2.bound = True


def attempt_binding_respect_particle_type(p1: Particle, p2: Particle, maxdist: float) -> None:

    # check for bound
    if p1.bound or p2.bound:
        return

    if p1.particle_type not in p2.binding_partners:
        return

    if p2.particle_type not in p1.binding_partners:
        return

    # measure distance to determine whether to bind
    if distance(*p1.pos, *p2.pos) < maxdist:
        p1.bound = True
        p2.bound = True


def demo_double_for(
    n_steps: int = 1000,
    xsize: int = 800,
    ysize: int = 800,
    n: int = 2000,
) -> None:
    """Baseline: compare every particle with every other particle.

    The straightforward nested loop over all pairs. Correct, easy to read, and
    quadratic: doubling ``n`` makes it roughly four times slower. Use it as the
    reference the other variants are compared against.

    Args:
        n_steps: How many simulation steps to run.
        xsize: Canvas width in pixels.
        ysize: Canvas height in pixels.
        n: Number of particles.

    """
    screen = Canvas("test", xsize, ysize)
    pen = Writer(screen)

    x = []
    y = []
    bound = []
    boundto = []

    for _ in range(n):
        x.append(rnd.randint(0, xsize))
        y.append(rnd.randint(0, ysize))
        bound.append(False)
        boundto.append(-1)

    for _ in range(n_steps):
        for i in range(n):
            dx = rnd.randint(-4, 4)
            dy = rnd.randint(-4, 4)

            if x[i] + dx > 0 and x[i] + dx < xsize and y[i] + dy > 0 and y[i] + dy < ysize and not bound[i]:
                x[i] += dx
                y[i] += dy

        maxdist = 5
        for i in range(n):
            for j in range(n):
                dist = math.sqrt((x[i] - x[j]) ** 2 + (y[i] - y[j]) ** 2)
                if dist < maxdist and not bound[i] and not bound[j] and i != j:
                    bound[i] = True
                    bound[j] = True

        for i in range(n):
            if rnd.random() < 0.05:
                bound[i] = False
                boundto[i] = False

        for i in range(n):
            col = Color.red if bound[i] else Color.green

            pen.draw_circle(x[i], y[i], 3, col, True)

        screen.update()
        screen.pause(0)
        screen.clear()


def demo_iterator_single(
    n_steps: int = 1000,
    xsize: int = 800,
    ysize: int = 800,
    n: int = 2000,
) -> None:
    """Same simulation, but only nearby pairs are checked.

    Uses ``get_close_pairs`` to iterate candidate pairs from a grid instead of
    all pairs, and a ``Particle`` dataclass instead of parallel lists. This is
    the version to copy for your own project.

    Args:
        n_steps: How many simulation steps to run.
        xsize: Canvas width in pixels.
        ysize: Canvas height in pixels.
        n: Number of particles.

    """
    maxdist = 5
    gridsize = ceil(1.5 * maxdist)

    screen = Canvas("test", xsize, ysize)
    pen = Writer(screen)

    particles = [Particle.from_random(xsize, ysize) for _ in range(n)]

    for _ in range(n_steps):
        for particle in particles:
            particle.rw_step_in_box(xsize, ysize)

        xs = [p.x for p in particles]
        ys = [p.y for p in particles]

        for i, j in get_close_pairs(xs, ys, gridsize):
            attempt_binding(particles[i], particles[j], maxdist)

        for particle in particles:
            particle.attempt_unbinding()

        for particle in particles:
            pen.draw_circle(*particle.pos, particle.radius, particle.color, filled=True)

        screen.update()
        screen.pause(0)
        screen.clear()


def demo_decorator_single(
    n_steps: int = 1000,
    xsize: int = 800,
    ysize: int = 800,
    n: int = 2000,
) -> None:
    """Nearby pairs again, this time through the decorator helper.

    ``@apply_to_close_pairs`` calls the decorated function once per candidate
    pair, so you write the pair logic and NaNoPy owns the iteration. Same
    result as ``collision_iterator_single``, different style.

    Args:
        n_steps: How many simulation steps to run.
        xsize: Canvas width in pixels.
        ysize: Canvas height in pixels.
        n: Number of particles.

    """
    screen = Canvas("test", xsize, ysize)
    pen = Writer(screen)

    x = []
    y = []
    bound = []
    boundto = []

    for _ in range(n):
        x.append(rnd.randint(0, xsize))
        y.append(rnd.randint(0, ysize))
        bound.append(False)
        boundto.append(-1)

    for _ in range(n_steps):
        for i in range(n):
            dx = rnd.randint(-4, 4)
            dy = rnd.randint(-4, 4)

            if x[i] + dx > 0 and x[i] + dx < xsize and y[i] + dy > 0 and y[i] + dy < ysize and not bound[i]:
                x[i] += dx
                y[i] += dy

        maxdist = 5

        @apply_to_close_pairs(x, y, ceil(maxdist * 1.5))
        def _apply_pair(i: int, j: int, max_distance: float = maxdist) -> None:  # pyright: ignore[reportUnusedFunction]
            dist = math.sqrt((x[i] - x[j]) ** 2 + (y[i] - y[j]) ** 2)
            if dist < max_distance and not bound[i] and not bound[j] and i != j:
                bound[i] = True
                bound[j] = True

        for i in range(n):
            if rnd.random() < 0.05:
                bound[i] = False
                boundto[i] = False

        for i in range(n):
            col = Color.red if bound[i] else Color.green

            pen.draw_circle(x[i], y[i], 3, col, True)

        screen.update()
        screen.pause(0)
        screen.clear()


def demo_iterator_dual_ab(
    n_steps: int = 1000,
    xsize: int = 800,
    ysize: int = 800,
    n: int = 2000,
) -> None:
    """Two particle species that only bind across groups.

    ``get_close_pairs(..., xs_b=, ys_b=)`` pairs group A against group B, so
    A-A and B-B pairs are never even considered. Each group has its own bound
    and unbound colors.

    Args:
        n_steps: How many simulation steps to run.
        xsize: Canvas width in pixels.
        ysize: Canvas height in pixels.
        n: Number of particles *per group*.

    """
    maxdist = 5
    gridsize = ceil(1.5 * maxdist)

    screen = Canvas("test", xsize, ysize)
    pen = Writer(screen)

    particles = [Particle.from_random(xsize, ysize) for _ in range(n)]
    particles_b = [
        Particle.from_random(
            xsize,
            ysize,
            color_bound=Color.css("cadetblue"),
            color_unbound=Color.css("darkmagenta"),
        )
        for _ in range(n)
    ]

    for _ in range(n_steps):
        for particle in particles:
            particle.rw_step_in_box(xsize, ysize)
        for particle in particles_b:
            particle.rw_step_in_box(xsize, ysize)

        xs = [p.x for p in particles]
        ys = [p.y for p in particles]
        x2s = [p.x for p in particles_b]
        y2s = [p.y for p in particles_b]

        for i, j in get_close_pairs(xs, ys, gridsize, xs_b=x2s, ys_b=y2s):
            attempt_binding(particles[i], particles_b[j], maxdist)

        for particle in particles:
            particle.attempt_unbinding()
        for particle in particles_b:
            particle.attempt_unbinding()

        for particle in particles:
            pen.draw_circle(*particle.pos, particle.radius, particle.color, filled=True)

        for particle in particles_b:
            pen.draw_circle(*particle.pos, particle.radius, particle.color, filled=True)

        screen.update()
        screen.pause(0)
        screen.clear()


def demo_decorator_dual_ab(
    n_steps: int = 1000,
    xsize: int = 800,
    ysize: int = 800,
    n: int = 2000,
) -> None:
    """Two species binding across groups, written with the decorator.

    The ``xs_b``/``ys_b`` form of ``@apply_to_close_pairs``: index ``i`` refers
    to group A and index ``j`` to group B inside the decorated function.

    Args:
        n_steps: How many simulation steps to run.
        xsize: Canvas width in pixels.
        ysize: Canvas height in pixels.
        n: Number of particles *per group*.

    """
    screen = Canvas("test", xsize, ysize)
    pen = Writer(screen)

    x = []
    y = []
    bound = []
    boundto = []

    x2 = []
    y2 = []
    bound2 = []
    boundto2 = []

    for _ in range(n):
        x.append(rnd.randint(0, xsize))
        y.append(rnd.randint(0, ysize))
        bound.append(False)
        boundto.append(-1)

        x2.append(rnd.randint(0, xsize))
        y2.append(rnd.randint(0, ysize))
        bound2.append(False)
        boundto2.append(-1)

    for _ in range(n_steps):
        for i in range(n):
            dx = rnd.randint(-4, 4)
            dy = rnd.randint(-4, 4)

            if x[i] + dx > 0 and x[i] + dx < xsize and y[i] + dy > 0 and y[i] + dy < ysize and not bound[i]:
                x[i] += dx
                y[i] += dy

            dx = rnd.randint(-4, 4)
            dy = rnd.randint(-4, 4)

            if x2[i] + dx > 0 and x2[i] + dx < xsize and y2[i] + dy > 0 and y2[i] + dy < ysize and not bound2[i]:
                x2[i] += dx
                y2[i] += dy

        maxdist = 5

        @apply_to_close_pairs(x, y, ceil(maxdist * 1.5), xs_b=x2, ys_b=y2)
        def _apply_pair(i: int, j: int, max_distance: float = maxdist) -> None:  # pyright: ignore[reportUnusedFunction]
            dist = math.sqrt((x[i] - x2[j]) ** 2 + (y[i] - y2[j]) ** 2)
            if dist < max_distance and not bound[i] and not bound2[j]:
                bound[i] = True
                bound2[j] = True

        for i in range(n):
            if rnd.random() < 0.05:
                bound[i] = False
                boundto[i] = False

        for i in range(n):
            if rnd.random() < 0.05:
                bound2[i] = False
                boundto2[i] = False

        for i in range(n):
            col = Color.red if bound[i] else Color.green

            pen.draw_circle(x[i], y[i], 3, col, True)

        for i in range(n):
            col = Color.red if bound2[i] else Color.cyan

            pen.draw_circle(x2[i], y2[i], 3, col, True)

        screen.update()
        screen.pause(0)
        screen.clear()


def demo_iterator_dual_by_particle_type(
    n_steps: int = 1000,
    xsize: int = 800,
    ysize: int = 800,
    n: int = 2000,
) -> None:
    """One mixed list of particles that decide themselves whether they may bind.

    All particles live in a single list and carry a ``particle_type`` plus a
    list of ``binding_partners``; the binding rule rejects pairs that are not
    allowed. This scales to more than two species, unlike the A/B variants.

    Args:
        n_steps: How many simulation steps to run.
        xsize: Canvas width in pixels.
        ysize: Canvas height in pixels.
        n: Number of particles *per species*.

    """
    maxdist = 5
    gridsize = ceil(1.5 * maxdist)

    screen = Canvas("test", xsize, ysize)
    pen = Writer(screen)

    particles_a = [
        Particle.from_random(
            xsize,
            ysize,
            particle_type=0,
            binding_partners=(1,),
        )
        for _ in range(n)
    ]
    particles_b = [
        Particle.from_random(
            xsize,
            ysize,
            color_bound=Color.css("cadetblue"),
            color_unbound=Color.css("darkmagenta"),
            particle_type=1,
            binding_partners=(0,),
        )
        for _ in range(n)
    ]

    particles = particles_a + particles_b

    for _ in range(n_steps):
        for particle in particles:
            particle.rw_step_in_box(xsize, ysize)

        xs = [p.x for p in particles]
        ys = [p.y for p in particles]

        for i, j in get_close_pairs(xs, ys, gridsize):
            attempt_binding_respect_particle_type(particles[i], particles[j], maxdist)

        for particle in particles:
            particle.attempt_unbinding()

        for particle in particles:
            pen.draw_circle(*particle.pos, particle.radius, particle.color, filled=True)

        screen.update()
        screen.pause(0)
        screen.clear()


def demo(
    n_steps: int = 500,
    xsize: int = 800,
    ysize: int = 800,
    n: int = 500,
) -> None:
    """Run every collision variant in turn and print how long each one took.

    The variants all simulate the same thing, so the printed timings show what
    the pair-selection strategy costs. Each variant opens its own window; close
    it to skip ahead to the next one.

    Args:
        n_steps: How many simulation steps to run per variant.
        xsize: Canvas width in pixels.
        ysize: Canvas height in pixels.
        n: Number of particles per variant.

    """
    kwargs = {"n_steps": n_steps, "xsize": xsize, "ysize": ysize, "n": n}
    demos = [
        demo_double_for,
        demo_iterator_single,
        demo_decorator_single,
        demo_iterator_dual_ab,
        demo_decorator_dual_ab,
        demo_iterator_dual_by_particle_type,
    ]

    for runner in demos:
        start = perf_counter()
        try:
            runner(**kwargs)
            elapsed = perf_counter() - start
            print(f"method {runner.__name__!s} took {elapsed:.3f} seconds for {n_steps} timesteps")
        finally:
            # Each benchmark owns one canvas. Release it before the next demo
            # reuses the "test" name and initializes a fresh mainloop runtime.
            NNP.stop()


if __name__ == "__main__":
    demo()
