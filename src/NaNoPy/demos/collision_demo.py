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

    @classmethod
    def from_random(cls, xsize:int, ysize:int) -> "Particle":
        return cls(x=randint(0, xsize), y=randint(0, ysize))

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
        return Color.red if self.bound else Color.green

        
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

def demo_double_for(n_steps:int=1000, xsize=800, ysize=800, n=2000):
    screen = Canvas("test",xsize,ysize)
    pen = Writer(screen)

    x = []
    y = []
    bound = []
    boundto = [] 

    for i in range(n):
        x.append(rnd.randint(0,xsize))
        y.append(rnd.randint(0,ysize))
        bound.append(False)
        boundto.append(-1)

    for _ in range(n_steps):
        

        for i in range(n):
            dx = rnd.randint(-4,4)
            dy = rnd.randint(-4,4)

            if x[i]+dx > 0 and x[i]+dx < xsize and y[i]+dy > 0 and y[i] + dy < ysize and not bound[i]:
                x[i] += dx
                y[i] += dy
        
        

        maxdist = 5
        #data = create_dictionary(x,y,maxdist*1.5,xsize,ysize)
        for i in range(n):
            for j in range(n):
                dist = math.sqrt((x[i]-x[j])**2 + (y[i]-y[j])**2)
                if dist < maxdist and not bound[i] and not bound[j] and i != j:
                    bound[i] = True
                    bound[j] = True
                

        for i in range(n):
            if rnd.random() < 0.05:
                bound[i] = False
                boundto[i] = False
                
        for i in range(n):
            if bound[i]:
                col = Color.red
            else:
                col = Color.green
            
            pen.draw_circle(x[i],y[i],3,col,True)
        
        screen.update()
        screen.pause(0)
        screen.clear()

def demo_decorator(n_steps:int=1000, xsize=800, ysize=800, n=2000):
    screen = Canvas("test",xsize,ysize)
    pen = Writer(screen)

    x = []
    y = []
    bound = []
    boundto = [] 

    for i in range(n):
        x.append(rnd.randint(0,xsize))
        y.append(rnd.randint(0,ysize))
        bound.append(False)
        boundto.append(-1)

    for _ in range(n_steps):
        

        for i in range(n):
            dx = rnd.randint(-4,4)
            dy = rnd.randint(-4,4)

            if x[i]+dx > 0 and x[i]+dx < xsize and y[i]+dy > 0 and y[i] + dy < ysize and not bound[i]:
                x[i] += dx
                y[i] += dy
        
        

        maxdist = 5
        #data = create_dictionary(x,y,maxdist*1.5,xsize,ysize)
            
            
        @apply_to_close_pairs(x, y, ceil(maxdist * 1.5))
        def func(i,j):
            dist = math.sqrt((x[i]-x[j])**2 + (y[i]-y[j])**2)
            if dist < maxdist and not bound[i] and not bound[j] and i != j:
                bound[i] = True
                bound[j] = True

        for i in range(n):
            if rnd.random() < 0.05:
                bound[i] = False
                boundto[i] = False
                
        for i in range(n):
            if bound[i]:
                col = Color.red
            else:
                col = Color.green
            
            pen.draw_circle(x[i],y[i],3,col,True)
        
        screen.update()
        screen.pause(0)
        screen.clear()

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

        for i, j in get_close_pairs(xs,ys, gridsize):
            attempt_binding(particles[i], particles[j], maxdist)

        for particle in particles:
            particle.attempt_unbinding()
               
        for particle in particles:
            pen.draw_circle(*particle.pos, particle.radius, particle.color, filled=True)
        
        screen.update()
        screen.pause(0)
        screen.clear()

if __name__ == "__main__":
    n_steps = 1000

    demos = [
        # demo_double_for, 
        demo_decorator, 
        demo_iterator
    ]

    for demo in demos:
        start = perf_counter()
        demo(n_steps)
        elapsed = perf_counter() - start
        print(f"method {str(demo)} took {elapsed:.3f} seconds for {n_steps} timesteps")
