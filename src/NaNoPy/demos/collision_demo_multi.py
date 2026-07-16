from NaNoPy import Canvas, Writer, Color
from random import randint, random
from dataclasses import dataclass
from math import sqrt
from time import perf_counter
from math import ceil
import random as rnd
import math
from NaNoPy import get_close_pairs, apply_to_close_pairs


@dataclass
class Particle:
    x:int
    y:int
    bound:bool=False
    stepsize:int=4
    p_unbind = 0.05
    radius = 3
    color_bound = Color.red
    color_unbound = Color.green

    @classmethod
    def from_random(cls, xsize:int, ysize:int, color_bound=color_bound, color_unbound=color_unbound) -> "Particle":
        return cls(x=randint(0, xsize), y=randint(0, ysize), color_bound=color_bound, color_unbound=color_unbound)

    @property
    def pos(self) -> tuple[int, int]:
        return self.x, self.y

    def rw_step_in_box(self, xsize:int, ysize:int) -> None:
        """
        Slightly changed from original logic. Now particles can rejects part of 
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
    def color(self):
        return self.color_bound if self.bound else self.color_unbound

        
def distance(x1:int|float, y1:int|float, x2:int|float, y2:int|float) -> float:
    return sqrt((x1 - x2)**2 + (y1 - y2)**2)

def attempt_binding(p1:Particle, p2:Particle, maxdist:float):

    # check for bound
    if p1.bound or p2.bound:
        return

    # measure distance to determine whether to bind
    if distance(*p1.pos, *p2.pos) < maxdist:
        p1.bound = True
        p2.bound = True

def demo_iterator(n_steps:int=1000, xsize=800, ysize=800, n=2000):

    maxdist = 5
    gridsize = ceil(1.5 * maxdist)

    screen = Canvas("test",xsize,ysize)
    pen = Writer(screen)


    particles = [Particle.from_random(xsize, ysize) for _ in range(n)]

    for _ in range(n_steps):

        for particle in particles:
            particle.rw_step_in_box(xsize, ysize)

        xs = [p.x for p in particles]
        ys = [p.y for p in particles]

        for i, j in get_close_pairs(xs,ys,gridsize):
            attempt_binding(particles[i], particles[j], maxdist)

        for particle in particles:
            particle.attempt_unbinding()
               
        for particle in particles:
            pen.draw_circle(*particle.pos, particle.radius, particle.color, filled=True)
        
        screen.update()
        screen.pause(0)
        screen.clear()

def demo_iterator_dual_particles(n_steps:int=1000, xsize=800, ysize=800, n=2000):

    maxdist = 5
    gridsize = ceil(1.5 * maxdist)

    screen = Canvas("test",xsize,ysize)
    pen = Writer(screen)


    particles = [Particle.from_random(xsize, ysize) for _ in range(n)]
    particlesB = [Particle.from_random(xsize, ysize, color_bound=Color.css("coral"), color_unbound=Color.css("chartreuse")) for _ in range(n)]

    for _ in range(n_steps):

        for particle in particles:
            particle.rw_step_in_box(xsize, ysize)
        for particle in particlesB:
            particle.rw_step_in_box(xsize, ysize)

        xs = [p.x for p in particles]
        ys = [p.y for p in particles]
        x2s = [p.x for p in particlesB]
        y2s = [p.y for p in particlesB]

        for i, j in get_close_pairs(xs,ys,gridsize,x2s=x2s,y2s=y2s):
            attempt_binding(particles[i], particlesB[j], maxdist)

        for particle in particles:
            particle.attempt_unbinding()
        for particle in particlesB:
            particle.attempt_unbinding()

        for particle in particles:
            pen.draw_circle(*particle.pos, particle.radius, particle.color, filled=True)
        
        for particle in particlesB:
            pen.draw_circle(*particle.pos, particle.radius, particle.color, filled=True)
        
        screen.update()
        screen.pause(0)
        screen.clear()

if __name__ == "__main__":
    n_steps = 500

    demos = [
        demo_iterator,
        demo_iterator_dual_particles

    ]

    for demo in demos:
        start = perf_counter()
        demo(n_steps)
        elapsed = perf_counter() - start
        print(f"method {str(demo)} took {elapsed:.3f} seconds for {n_steps} timesteps")
